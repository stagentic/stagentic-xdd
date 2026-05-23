---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0003 — Pin model versions; treat upgrades as deliberate migrations

**Status:** Proposed

## Context

The TDAB harness in [ADR 0001](0001-start-with-tdab-and-vanilla-pytest.md) depends on model behaviour twice over: the *Critic* uses `claude -p` to grade transcripts against a scorecard prompt, and (once the stub is swapped out) the agentic *When* step uses `claude -p` to drive Red-Green-Refactor on the fixture. In both cases, the active model is part of the system under test.

The motivating incident is documented in [*Taming Claude Code one agentic test at a time*](https://antonymarcano.substack.com/p/taming-claude-code-one-agentic-test). In summary: when Opus 4.7 released, a previously-green regression suite began failing. The cause was not a guidance change — it was that the newer model *reinterpreted* the existing guidance. A single word ("orchestrate") in a skill description caused Opus 4.7 to take on test-coordination responsibilities that should have stayed with the background Python process, producing unwanted API calls and broken workflows. The author's summary: *"I spent an hour scratching my head as to why everything seemed like it was falling apart."*

The general shape of the problem: without a pinned model, a failing scenario could be a guidance bug, a fixture bug, *or* a silent model behaviour change — and you cannot tell which. The regression suite only provides value when the model underneath it is held constant; otherwise green and red carry no signal.

## Decision

Pin the model identifiers that scenarios in this repo are validated against, and treat any bump as a deliberate migration rather than a transparent upgrade.

1. **Record the pinned model identifier(s) in this repo.** Different scenarios may target different tiers (Opus for the agentic When, Sonnet or Haiku for the Critic), so the pin is a small map of tier → model ID (e.g. `opus: claude-opus-4-7`, `sonnet: claude-sonnet-4-6`) rather than a single value. Exact filename and format are settled when the pytest harness lands.

2. **Set the model explicitly at run time, but defer to existing env vars.** Before invoking `claude -p`, the harness sets `ANTHROPIC_DEFAULT_OPUS_MODEL` (and sibling vars for Sonnet/Haiku) from the pin — *only if* those vars are not already set. An externally-set value wins and is treated as a deliberate override (see decision 4). Default behaviour stays reproducible across contributors; migration spikes can override without editing files.

3. **Surface mismatch loudly.** Where the underlying client reports the resolved model, the harness compares it to the pin and fails the run on a mismatch (unless an override is in effect, in which case the harness prints a clearly-marked banner instead).

4. **Validate candidate models via env-var override, without committing.** Setting `ANTHROPIC_DEFAULT_OPUS_MODEL` (or the relevant tier var) in the shell to a candidate model tells the harness to use it; the harness reports the run as a non-pinned spike. Run the full scenario suite under the override before touching the pin file. The committed pin stays unchanged through this stage.

5. **Bump the committed pin only after override-validated green.** If the spike passes, bump the pin file in a dedicated branch (no scenario changes in the same PR), re-run the suite once more to confirm reproducibility, capture release-notes triage and any guidance edits in the commit message, and merge. If the spike fails, investigate; the committed pin stays where it is.

6. **Detect new model availability explicitly.** Don't rely on the default rolling forward. A periodic review of Anthropic model release notes triggers a spike branch when warranted, well before the pinned model approaches end-of-life.

7. **Roll back by reverting the pin commit.** Because the pin lives in-repo and the harness reads it at run time, restoring a known-good model is `git revert` of the bump commit. No special tooling.

CLI-version pinning is a closely related but separate decision; see [ADR 0002](0002-pin-claude-code-cli-version.md). The override-then-bump migration workflow is intentionally parallel between the two ADRs.

## Consequences

- Auditor and Critic runs become comparable across time and across contributors: a fail is a fail for guidance/fixture reasons, not because Anthropic shipped a new default overnight.
- Override-driven spikes never appear in commit history. The committed pin always reflects a known-green state; migration noise stays in the shell session.
- The harness prints a clearly-marked banner when running under override, so override results aren't mistaken for pinned-green signals in transcripts.
- Pinned models will eventually be deprecated upstream; we must migrate before EOL, not after. A periodic release-notes review (see decision 6) is the mechanism that keeps this from being a fire-drill.
- Each scenarios-validated PR is implicitly validated against the pin in effect on its branch; reviewers can read the pin to know which model produced the green run.
- Guidance written for one model may need editing when the pin moves — the bump commit captures those edits in one place rather than scattering them.
- The harness has a hard dependency on the contributor's API access including the pinned model tiers. If a contributor lacks access to (e.g.) Opus, scenarios that target Opus cannot be run locally.

## Alternatives considered

- **Rely on the Anthropic default model.** Rejected: defaults roll forward silently. The Opus 4.7 incident above is the canonical example of why this loses the ability to distinguish a guidance bug from a model behaviour change.
- **Pin a single model for the whole suite.** Rejected: the Critic does not need Opus for scorecard grading, and forcing one tier across all scenarios either inflates cost (Opus everywhere) or weakens the agentic When (Haiku everywhere). A per-tier pin is the minimum that lets each scenario use the right tier.
- **Pin per-test in test bodies via API arguments.** Rejected as too distributed: a single environment-level pin is easier to audit ("what model did this branch run against?") and easier to override for migration spikes than one scattered across many files.
- **Pin only the major-version family (e.g. "Opus 4.x") rather than a specific patch.** Rejected for the same reason as the [ADR 0002](0002-pin-claude-code-cli-version.md) auto-update rejection: minor-version model updates can and do change behaviour materially, and the suite's value depends on holding that constant.
- **Use git branches alone to swap pins for migration spikes.** Rejected: that requires committing the candidate pin to test it, coupling each exploratory run to commit history. An env override keeps spikes ephemeral and the committed pin always at known-green.
