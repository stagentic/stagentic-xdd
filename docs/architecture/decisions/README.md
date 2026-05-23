---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# Architecture Decisions

Architecture Decision Records (ADRs) capture the *why* behind significant design choices in stagentic-tdd. Each ADR records the context, the decision, and the alternatives considered.

See [0000](0000-use-adrs-to-record-decisions.md) for more on ADRs, the rationale, the format, statuses, and conventions.

## How to add an ADR

1. Copy `TEMPLATE.md` to `NNNN-short-slug.md` (next available number).
2. Fill in the sections.
3. Set status to `Proposed`.
4. Add a row in the index below.

## Index

| # | Title | Status |
|---|---|---|
| [0000](0000-use-adrs-to-record-decisions.md) | Use ADRs to record decisions | Proposed |
| [0001](0001-start-with-tdab-and-vanilla-pytest.md) | Start development by applying the TDAB pattern with vanilla pytest | Proposed |
| [0002](0002-pin-claude-code-cli-version.md) | Pin the Claude Code CLI version; treat upgrades as deliberate migrations | Proposed |
| [0003](0003-pin-model-versions.md) | Pin model versions; treat upgrades as deliberate migrations | Proposed |
| [0004](0004-structure-agent-control-with-guidance-guardrails-and-gateways.md) | Structure agent control through guidance, guardrails, and gateways | Proposed |
