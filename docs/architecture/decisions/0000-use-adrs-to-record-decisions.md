---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0000 — Use ADRs to record decisions

**Status:** Proposed

## Context

We need to capture decisions about how stagentic-tdd is built — staging, scope choices, packaging, naming, and so on — as durable reference material. The decisions matter most when later contributors (or our future selves) want to know *why* something was done, not just *what* was done. Git history shows the what; the why often lives in PR descriptions, chat, or memory that scatters and rots.

These docs live with the stagentic-tdd project. The format is designed to be durable — ADRs do not link to files outside this repository — so they remain coherent across forks, mirrors, or future extractions.

## Decision

Adopt ADRs (Architecture Decision Records) as the journal format for stagentic-tdd. Each significant decision gets its own numbered file under `decisions/`.

- One decision per file. Numbered sequentially from 0000 upwards.
- Standard sections: Status, Context, Decision, Consequences, Alternatives considered.
- Statuses: `Proposed`, `Accepted`, `Rejected`, `Superseded`, `Deprecated`.
- Append-only. Later decisions can supersede earlier ones, but the earlier file remains so the reasoning trail is intact.
- Entries are written when the decision is being made or has just been made — not reconstructed later.
- Portability rule (carried in every ADR's frontmatter): no links to files outside this project's docs folder. External web URLs are fine.

## Consequences

- Decisions get captured at the time they are made, while the alternatives are still live in conversation. The "why" is preserved.
- One file per decision keeps each entry focused and reviewable, and lets a single decision be superseded without disturbing the rest.
- Light overhead — a markdown file per decision, no tooling needed.
- The format is durable across forks and mirrors. ADRs link only within the repo and to external web URLs, so the reasoning trail stays intact regardless of where the repo lives.
- Risk: if entries are written retrospectively (after the fact), they tend to read as justification rather than deliberation. Mitigation: write while the decision is still uncertain, mark `Proposed` until validated, and keep `Alternatives considered` honest.

## Alternatives considered

- **Single decision-log file.** One running document with chronological entries. Lower overhead initially but harder to navigate as the project grows; entries cannot be selectively superseded, and the file gets noisy.
- **Inline in plans / READMEs.** Skip a separate journal and let the rationale live alongside the current-state docs. Loses the *why* over time — plans drift to reflect current state, and the alternatives that were considered get edited out as they become irrelevant.
- **No journal.** The default. Loses the reasoning trail entirely.

## Reference

- Michael Nygard, "Documenting Architecture Decisions" (2011): https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
