---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0003 — Pin model versions; treat upgrades as deliberate migrations

**Status:** Accepted

## Context

The TDAB harness in [ADR 0001](0001-start-with-tdab-and-vanilla-pytest.md) depends on model behaviour twice over: the *Critic* uses `claude -p` to grade transcripts against a scorecard prompt, and (once the stub is swapped out) the agentic *When* step uses `claude -p` to drive Red-Green-Refactor on the fixture. In both cases, the active model is part of the system under test.

The motivating incident is documented in [*Taming Claude Code one agentic test at a time*](https://antonymarcano.substack.com/p/taming-claude-code-one-agentic-test). In summary: when Opus 4.7 released, a previously-green regression suite began failing. The cause was not a guidance change — it was that the newer model *reinterpreted* the existing guidance. A single word ("orchestrate") in a skill description caused Opus 4.7 to take on test-coordination responsibilities that should have stayed with the background Python process, producing unwanted API calls and broken workflows. The author's summary: *"I spent an hour scratching my head as to why everything seemed like it was falling apart."*

The general shape of the problem: without a pinned model, a failing scenario could be a guidance bug, a fixture bug, *or* a silent model behaviour change — and you cannot tell which. The regression suite only provides value when the model underneath it is held constant; otherwise green and red carry no signal.

## Decision

Pin the model identifiers that scenarios in this repo are validated against, and treat any bump as a deliberate migration rather than a transparent upgrade.

1. **Declare the pin in `.claude/settings.json`.** The `env` block maps each tier to a full model ID:
   ```json
   {
     "env": {
       "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-7",
       "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-4-6",
       "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5-20251001"
     }
   }
   ```
   Claude Code injects these into the environment of every process it spawns, including the pytest harness and all `claude -p` invocations. No harness code is required.

2. **Validate candidate models by editing and running.** Update the model IDs in `.claude/settings.json` and run the full scenario suite. If the suite passes, commit and done. If it fails, branch — make whatever guidance changes are needed to get green, then merge (or submit a PR) with the pin bump and those changes together.

3. **Detect new model availability explicitly.** Don't rely on defaults rolling forward. A periodic review of Anthropic model release notes triggers a spike branch when warranted, well before the pinned model approaches end-of-life.

4. **Roll back by reverting the bump commit.** Restoring a known-good model is `git revert` of the bump commit. No special tooling.

CLI-version pinning is a closely related but separate decision; see [ADR 0002](0002-pin-claude-code-cli-version.md).

## Consequences

- Auditor and Critic runs become comparable across time and across contributors: a fail is a fail for guidance/fixture reasons, not because Anthropic shipped a new default overnight.
- A candidate that passes immediately needs no branch — edit, run, commit. A branch is only opened when the suite fails and guidance changes are needed alongside the pin bump.
- Pinned models will eventually be deprecated upstream; we must migrate before EOL, not after. A periodic release-notes review (see decision 3) is the mechanism that keeps this from being a fire-drill.
- Each scenarios-validated PR is implicitly validated against the pin in effect on its branch; reviewers can read `.claude/settings.json` to know which model produced the green run.
- Guidance written for one model may need editing when the pin moves — the bump commit captures those edits in one place rather than scattering them.
- Contributors without API access to a pinned model tier cannot run scenarios that target that tier locally.

## Alternatives considered

- **Rely on the Anthropic default model.** Rejected: defaults roll forward silently. The Opus 4.7 incident above is the canonical example of why this loses the ability to distinguish a guidance bug from a model behaviour change.
- **Pin a single model for the whole suite.** Rejected: the Critic does not need Opus for scorecard grading, and forcing one tier across all scenarios either inflates cost (Opus everywhere) or weakens the agentic When (Haiku everywhere). A per-tier pin is the minimum that lets each scenario use the right tier.
- **Pin per-test in test bodies via API arguments.** Rejected as too distributed: a single in-repo declaration in `.claude/settings.json` is easier to audit ("what model did this branch run against?") and easier to override for migration spikes than pins scattered across many files.
- **Pin only the major-version family (e.g. "Opus 4.x") rather than a specific patch.** Rejected for the same reason as the [ADR 0002](0002-pin-claude-code-cli-version.md) auto-update rejection: minor-version model updates can and do change behaviour materially, and the suite's value depends on holding that constant.
- **Use a shell env-var override to test candidates without committing.** Not needed: updating `.claude/settings.json` on a branch and running the suite is simpler — a failing branch is abandoned, a passing branch becomes the PR. No shell gymnastics required.
- **Use the `model` key in `.claude/settings.json`.** Rejected: this sets a single model for the whole Claude Code session. The harness invokes `claude -p` in different tiers for different steps (e.g. Opus for the agentic When, Sonnet or Haiku for the Critic); a single-value setting cannot express per-tier pinning. The per-tier env vars in the `env` block are the minimum that covers this distinction.
- **Enforce the pin via a harness fixture (read pin file, compare resolved model, fail on mismatch).** Rejected: enforcement is not needed. `.claude/settings.json` always injects the pinned vars into every spawned process — there is no path to a wrong model unless the contributor deliberately overrides via shell env, which is the intentional spike case.
