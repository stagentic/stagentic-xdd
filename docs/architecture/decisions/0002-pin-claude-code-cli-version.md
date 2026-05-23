---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0002 — Pin the Claude Code CLI version; treat upgrades as deliberate migrations

**Status:** Proposed

## Context

The TDAB harness in [ADR 0001](0001-start-with-tdab-and-vanilla-pytest.md) runs scenarios against the `claude` CLI — both directly (the agentic *When* step) and indirectly (the *Critic* invokes `claude -p` to grade transcripts). ADR 0001 already flagged the gap: *"Reproducibility of critic runs depends on the CLI surface staying stable; pinning strategy TBD."* This ADR closes that gap.

The motivating incident is documented in [*Your coding agents just broke yet again*](https://antonymarcano.substack.com/p/your-coding-agents-just-broke-yet). In summary: an unannounced Claude Code CLI auto-update silently changed the semantics of the `Agent()` tool — from creating isolated named subagents to creating forks that inherited the full parent conversation history (in one observed case ~242k cached tokens). Same call, different result, no notification. Concrete fallout included:

- Subagents recognised they were test subjects from inherited context and altered their reasoning, invalidating the regression suite's purpose.
- A forked agent attempted fork-only operations and ran inherited shell commands (e.g. `git stash pop`), causing the harness to fail in ways unrelated to the scenario under test.
- Identical calls behaved differently between fresh sessions and parent-forked sessions, breaking reproducibility.

In short, the CLI is a non-deterministic dependency that can change underneath us between one test run and the next. Scenarios that passed yesterday may fail today for reasons unrelated to the guidance being tested.

The install path for `claude` is environment-specific (host package manager, npm, native installer, container build, mise/asdf, etc.) and outside the scope of this ADR. What this repo *can* do is record the required version against which its scenarios have been validated and have the harness enforce that pin at run time. Environment-specific implementation guidance lives outside the ADRs.

## Decision

Pin the Claude Code CLI version that scenarios in this repo are validated against, and treat any bump as a deliberate migration rather than a transparent upgrade.

1. **Record the pinned version in this repo.** A single source-of-truth file (exact filename to be settled when the pytest harness lands — likely `.tool-versions` or a small `versions.toml` at repo root) records the `claude` CLI version the suite is known-green against.

2. **Surface mismatch loudly at run time.** The harness reads the pinned version on start-up and compares it to `claude --version`. A mismatch fails the run with a clear message — never a silent pass.

3. **Validate candidate versions via runtime override, without committing.** A dedicated environment variable (e.g. `STAGENTIC_CLI_VERSION_OVERRIDE`) tells the harness to compare against an override value instead of the file-pinned value, and to print a clearly-marked banner identifying the run as a non-pinned spike. A migration begins by installing the candidate `claude` version locally, setting the override, and running the full scenario suite. The committed pin stays unchanged through this stage; override-driven spikes leave no permanent artefacts.

4. **Bump the committed pin only after override-validated green.** If the override spike passes, bump the pin file in a dedicated branch (no scenario changes in the same PR), re-run the suite once more to confirm reproducibility, capture release-notes triage in the commit message, and merge. If the spike fails, investigate; the committed pin stays where it is.

5. **Detect new versions explicitly.** Don't rely on auto-update notifications. A periodic check (manual or scheduled) reviews available CLI releases and their changelogs; whoever runs the check opens an issue or branch if a bump is warranted.

6. **Roll back by reverting the pin commit.** Because the pin lives in-repo, restoring a known-good version is `git revert` of the bump commit followed by re-installing the indicated version in the dev environment. No special tooling.

Model-version pinning is a closely related but separate decision; see [ADR 0003](0003-pin-model-versions.md).

## Consequences

- A fresh checkout cannot run the scenario suite until the dev environment provides the pinned CLI version. The mismatch check makes this immediate rather than confusing.
- Whatever installs `claude` in a given environment (host package manager, container build, lockfile, etc.) needs to install the pinned version, or the harness refuses to run. Environment-specific install guidance lives outside the ADRs.
- Override-driven spikes never appear in commit history. The committed pin always reflects a known-green state; migration noise stays in the local working environment.
- The harness prints a clearly-marked banner when running under override, so override results aren't mistaken for pinned-green signals in transcripts or CI logs.
- CLI bug-fixes and improvements arrive on this repo's schedule, not upstream's. Some lag is the price of reproducibility.
- Each bump produces a small audit trail: the commit message records what changed upstream and which scenarios were re-run.

## Alternatives considered

- **Live with auto-update.** Rejected: the `Agent()` semantic change above demonstrates that silent CLI updates can invalidate scenarios with zero code change and no notification, which is exactly the regression failure mode the TDAB harness exists to prevent.
- **Pin only at install-time (build manifest, lockfile, container Dockerfile, etc.), not in the repo.** Rejected: an install-time pin is invisible to contributors using a different install mechanism, and the *repo's* scenarios are what need to declare what they were validated against. Install-time configuration in any environment should track this repo's pin, not the other way around.
- **Pin via an npm lockfile alone.** Rejected: not every install path goes through npm (e.g. native installers, mise/asdf, host package managers), so the pin should be expressed independently of install mechanism and enforced at run time by the harness.
- **Record the pinned version in prose only (e.g. in `README.md`).** Rejected: a prose pin can't be checked at run time, so mismatches stay silent until they cause confusing failures.
- **Use git branches alone to swap pins for migration spikes.** Rejected: that requires committing the candidate pin in order to test it, coupling each exploratory run to commit history. A runtime override keeps spikes ephemeral and the committed pin always at known-green.
