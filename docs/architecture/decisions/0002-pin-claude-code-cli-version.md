---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0002 — Pin the Claude Code CLI version; treat upgrades as deliberate migrations

**Status:** Accepted

## Context

The TDAB harness in [ADR 0001](0001-start-with-tdab-and-vanilla-pytest.md) runs scenarios against the `claude` CLI — both directly (the agentic *When* step) and indirectly (the *Critic* invokes `claude -p` to grade transcripts). ADR 0001 already flagged the gap: *"Reproducibility of critic runs depends on the CLI surface staying stable; pinning strategy TBD."* This ADR closes that gap.

The motivating incident is documented in [*Your coding agents just broke yet again*](https://antonymarcano.substack.com/p/your-coding-agents-just-broke-yet). In summary: an unannounced Claude Code CLI auto-update silently changed the semantics of the `Agent()` tool — from creating isolated named subagents to creating forks that inherited the full parent conversation history (in one observed case ~242k cached tokens). Same call, different result, no notification. Concrete fallout included:

- Subagents recognised they were test subjects from inherited context and altered their reasoning, invalidating the regression suite's purpose.
- A forked agent attempted fork-only operations and ran inherited shell commands (e.g. `git stash pop`), causing the harness to fail in ways unrelated to the scenario under test.
- Identical calls behaved differently between fresh sessions and parent-forked sessions, breaking reproducibility.

In short, the CLI is a non-deterministic dependency that can change underneath us between one test run and the next. Scenarios that passed yesterday may fail today for reasons unrelated to the guidance being tested.

## Decision

Pin the Claude Code CLI version that scenarios in this repo are validated against, and treat any bump as a deliberate migration rather than a transparent upgrade.

1. **Disable background auto-updates via `.claude/settings.json`.** Setting `DISABLE_AUTOUPDATER=1` in the project `env` block prevents the CLI from silently upgrading between runs for any contributor running via Claude Code in this project directory:
   ```json
   {
     "env": {
       "DISABLE_AUTOUPDATER": "1"
     }
   }
   ```

2. **Record the pinned version in `README.md`.** A Prerequisites section states the validated CLI version and the install command. This is the visible source of truth contributors read before getting started — no separate lockfile or harness check needed.

3. **Validate candidate versions by installing and running.** Install the candidate with `claude install <version>`, run the full scenario suite. If the suite passes, update the version in `README.md` and commit. If it fails, branch — make whatever guidance changes are needed to get green, then merge (or submit a PR) with the version bump and those changes together.

4. **Detect new versions explicitly.** Don't rely on auto-update notifications. A periodic review of Claude Code release notes triggers a migration when warranted, well before the pinned version approaches end-of-life.

5. **Roll back by reverting the bump commit and reinstalling the previous version.** The commit message records the version change, so `git revert` identifies what to reinstall. No special tooling.

Model-version pinning is a closely related but separate decision; see [ADR 0003](0003-pin-model-versions.md).

## Consequences

- Background auto-updates are disabled for all contributors running via Claude Code in this project directory. A contributor who runs `claude update` or manually installs a newer version is making a deliberate choice; the README makes the expected version visible.
- A fresh checkout surfaces the required version immediately via the Prerequisites section — no confusing harness failures before the contributor knows what version is needed.
- No harness code is required to enforce the pin.
- CLI bug-fixes and improvements arrive on this repo's schedule, not upstream's. Some lag is the price of reproducibility.
- Each bump produces a small audit trail: the commit records what changed upstream and which scenarios were re-run.

## Alternatives considered

- **Live with auto-update.** Rejected: the `Agent()` semantic change above demonstrates that silent CLI updates can invalidate scenarios with zero code change and no notification, which is exactly the regression failure mode the TDAB harness exists to prevent.
- **`versions.toml` at repo root plus a harness check that fails on version mismatch.** Rejected as over-engineering: `DISABLE_AUTOUPDATER` closes the silent-upgrade path that caused the original incident. A harness check adds code to maintain without meaningfully reducing the remaining risk (a contributor who deliberately installs a different version will read the README first).
- **`minimumVersion` in `.claude/settings.json`.** Rejected: this sets a floor that prevents downgrading, but auto-updates still move the version upward above the floor. It does not pin an exact version.
- **`autoUpdatesChannel: "stable"` in `.claude/settings.json`.** Rejected: this controls which release stream updates come from, not whether updates happen. The CLI still auto-updates within the stable channel.
- **Pin only at install-time (container Dockerfile, npm lockfile, mise/asdf, etc.), not in the repo.** Rejected: an install-time pin is invisible to contributors using a different install mechanism. The README pin is install-mechanism-agnostic and readable before any tooling is involved.
