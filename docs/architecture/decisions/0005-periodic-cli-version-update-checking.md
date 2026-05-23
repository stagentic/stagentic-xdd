---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0005 — Periodic Claude Code CLI version update checking

**Status:** Proposed

## Context

[ADR 0002](0002-pin-claude-code-cli-version.md) pins the Claude Code CLI version and disables background auto-updates. Decision 4 of that ADR calls for periodic explicit review of new CLI releases to avoid missing a significant improvement or being caught out by end-of-life. Without a mechanism to surface this, the review relies entirely on the developer remembering to check — which in practice means it doesn't happen.

The check needs to happen roughly once per day, but not on every session start — `/clear` is used multiple times per day and hooking into session lifecycle would be too frequent.

## Decision

To be determined.

### Options under consideration

#### A — Test suite wrapper script

A wrapper script is run instead of invoking pytest directly. Before handing off to the test runner, it checks a local gitignored date file (`.claude/.cli-version-check`). If the file records today's date, it skips the check. Otherwise it fetches the latest available CLI version from the npm registry, compares it to the pinned version in `README.md`, reports any change with a summary of what is new, and updates the date file. The check is a plain script — no agent behaviour, no TDAB scenarios required.

The check happens as a natural side-effect of running the suite rather than requiring a separate habit or invocation.

#### B — On-demand skill

A skill — provisionally `/check-cli-updates` — is invoked explicitly by the developer. It fetches the latest version from npm, compares to the pin in `README.md`, and reports what has changed. A local gitignored date file throttles it to once per day. `CLAUDE.md` notes the skill and suggests running it at the start of each working day.

This approach fits naturally into the stagentic-play ecosystem and could be validated with TDAB scenarios.

#### C — Remote scheduled agent

A scheduled agent (via the `/schedule` skill) runs daily on Anthropic-managed infrastructure, independently of any local session. It fetches the latest version and reports. As a cloud routine it cannot access local files directly — it would read the pinned version from the committed `README.md` on the default branch. Notification behaviour (whether a completed run is surfaced proactively or must be checked manually) is unclear from available documentation.

## Consequences

Whichever option is chosen:

- The check requires network access to the npm registry at run time.
- A local gitignored date file (options A and B) gives each contributor their own independent daily cadence.
- The committed pin in `README.md` is the source of truth the check reads against.

## Alternatives considered

To be determined.
