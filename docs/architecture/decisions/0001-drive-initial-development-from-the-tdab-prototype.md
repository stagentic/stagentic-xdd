---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0001 — Drive initial development from the tdab prototype

**Status:** Proposed

## Context

tdab is an existing prototype harness for outside-in, scenario-driven AI agent development. It provides a scenario format (Given / When / Then / Finally test files referencing per-step task files), a runner (`init-scenario`, the Stage Director coordination layer, sub-agent launching, transcript capture, scorecard evaluation), and a curated set of skills and AGENTS.md policies that govern the developer's Claude session. It was the workbench where TDAB (Test-Driven Agentic Behaviour) was developed by Antony Marcano — a technique adapted from TDD and BDD to drive agent behaviour rather than code.

The intent is to replace tdab with the stagentic-flow plugin once that plugin exists — and stagentic-flow is itself being developed with the help of this TDD plugin (stagentic-tdd). This is a deliberate bootstrap loop: tdab drives stagentic-tdd; stagentic-tdd drives stagentic-flow; stagentic-flow eventually replaces tdab.

We need a starting point. stagentic-flow does not yet exist as a plugin, and stagentic-tdd is being built from scratch. The question is what we use as the development environment and scenario runner during the bootstrap phase.

## Decision

Drive initial development from the tdab prototype. tdab serves as the temporary development environment and scenario runner during the bootstrap phase. The developer's Claude session starts in tdab; tdab's AGENTS.md and skills govern that session; subagents reach into the stagentic-tdd repo to perform implementation work.

## Consequences

- Work can begin immediately, without waiting for stagentic-flow to exist as a plugin.
- Spec content (scenarios, fixtures), production code, ADRs, and AGENTS.md all live in stagentic-tdd from day one. tdab hosts no project content; it provides only the runner and the developer's working context.
- No separate `stagentic-tdd-spec` repo is created. Creating a third repo before either plugin is loadable is overhead with no payoff; spec content can sit alongside the project code.
- tdab is not converted to a plugin. That option was considered and deprioritised: by the time a future arrangement might want it, stagentic-flow has replaced tdab as the runner, so the conversion would be wasted work.
- tdab is a prototype; rough edges become work items as scenarios demand them. Some such edges (e.g., path conventions in `init-scenario`) live in tdab itself and are out of scope for this project.
- Governance leak risk during the bootstrap phase: subagents launched from tdab read tdab's AGENTS.md by default, which can over-apply tdab-specific policies to work in stagentic-tdd. Mitigated by accountability and by scenario prompts that scope appropriately.
- Developer experience benefit: the developer stays in flow within tdab during bootstrap, rather than context-switching between repos. Switching costs — re-orienting, re-loading mental context, retooling the editor — are avoided until the work itself demands them.
- The arrangement is temporary by design. A later ADR will capture the switch when the stagentic-flow plugin exists and the developer environment moves to stagentic-tdd.

## Alternatives considered

- **Wait for the stagentic-flow plugin.** Block development until stagentic-flow exists as a loadable plugin. Rejected: chicken-and-egg — stagentic-flow itself benefits from being developed via scenarios, which need a runner to execute, and tdab is the available runner.
- **Build a minimal runner inside stagentic-tdd first.** Skip tdab; write a thin scenario runner inside stagentic-tdd as the first thing built. Rejected: large detour from the actual goal (the TDD plugin); tdab already provides a working harness, so the detour buys nothing on the critical path.
- **Develop stagentic-tdd without a scenario runner.** Build the TDD plugin using ordinary tooling, no outside-in scenarios. Rejected: stagentic-tdd is itself a TDD plugin; building it without TDD on the outer loop would be inconsistent with what it advocates.
