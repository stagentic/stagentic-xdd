---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0007 — Structure inner-loop scenarios as a task chain audited by a scorecard

**Status:** Accepted

## Context

ADR 0001 sets the strategy: TDAB with vanilla pytest, stub agent first then real, auditor first then critic. It does not specify the structural shape of a scenario.

The first scenario surfaced several decisions whose interplay is load-bearing:

- Where a *reference implementation* of a task's end-state lives, and how it relates to a real-agent run
- How scenarios compose — specifically, whether one task's reference implementation can serve directly as the next task's starting state
- How task descriptions and reference implementations coexist without the reference leaking to a future real agent
- What a scorecard row contains and how it survives the auditor → critic swap

Holding these together as one design is what makes the swaps tractable later.

## Decision

1. **Tasks are directories under `spec/tasks/`.** Each task is a unit of agent work, named by what it asks the agent to do (not by the outcome). `0-placeholder/` is the genesis state — no agent work involved.

2. **Each task's `scene/` holds a reference implementation** of the task's end-state — production code, tests, transcript. The fake agent copies it into the workspace; the auditor uses it as the reference for tree-diff. (Calling it a *reference implementation* rather than "the answer" is deliberate: when the critic lands, it will judge equivalence rather than byte-equality, and the reference becomes one valid example among many.)

3. **The reference implementation of one task serves as the starting state for the next task.** Scenarios chain through `scene/` directories. Scenario N starts by copying task N-1's `scene/` into the workspace, runs scenario N's agent, then audits against task N's own `scene/`. No separate `start/` directory per task — the chain carries the start state implicitly.

4. **The fake agent is a one-line `copytree`.** It mirrors the eventual real-agent contract — `task, in_workspace → transcript_path` — so the swap is a fixture-config change, not a test rewrite.

5. **A future `prompt.md` per task** will hold what the real agent gets told. The fake agent ignores it; the real agent reads only it (never `scene/`), so the reference implementation doesn't leak.

6. **Each scorecard row is `{characteristic, verify, failure}`:**
   - `characteristic` — prose statement of the expected behaviour
   - `verify(transcript, working_dir) -> bool` — auditor's deterministic check
   - `failure` — static prose printed when verify returns false

7. **The `characteristic` prose is the durable contract.** The auditor receives the full row (characteristic + verify + failure) — its *check strategy* for that characteristic. The critic receives only the `characteristic` prose, embedded in its scorecard prompt. Either evaluator can be swapped in without touching the test body.

## Consequences

- Scenarios are inspectable as filesystem state plus a list of characteristic strings — the test body is the manifest. The auditor's check strategies (verify + failure per characteristic) live in a helper, separable from the manifest so the manifest can feed either evaluator.
- Adding a scenario means adding the next task directory and a test that names the characteristics it expects.
- The chain encodes the system's evolution through TDD increments as data, not narrative.
- The characteristic-prose contract makes the auditor → critic swap a fixture-configuration change.
- Each task's `scene/` serves dual purpose: the reference implementation of its own completion *and* the starting state for the next task. This coupling is part of the design — as scenarios transition from scene to scene, the inner loop's story is told.
- The fake agent's `copytree` copies the entire `scene/` into the workspace. Anything in `scene/` that shouldn't be there (e.g., a transient `.venv/` from running `uv` inside `scene/` for manual verification) goes with it, polluting the workspace and breaking tree-diff. `copytree` may need an `ignore` argument.
- The two-faked-layers phase (fake agent + auditor) is intentional; the framework extracts under full determinism before any LLM is in the loop.

## Alternatives considered

- **`start/` and `end/` subdirectories per task** instead of just `scene/`: explicit start state per task, no chain dependency. Rejected: state duplication; the chain invariant becomes copy-and-verify rather than implicit.
- **`verify` returns a rich failure-detail string instead of a static `failure` field**: more informative diagnostics, but the failure prose then drifts per run and can't double as the critic prompt's "what should be true" line.
- **Scorecard as a markdown file separate from the test**: matches the TDAB prototyping environment (as seen in https://youtu.be/i3g9ZXiaqh0). Deferred until the critic genuinely needs the markdown form to embed in its prompt.
- **Named functions as scorecard rows** (with docstring as characteristic): more idiomatic Python; each check independently unit-testable. Rejected for now because it spreads each row across modules — the dict-literal manifest keeps the test body compact and lets a reader see all expectations at a glance.
- **Task names that describe the outcome** (e.g. `1-first-test-with-stub`): legible but prejudices the answer. Task-oriented names (`1-first-test-for-miles-to-km-converter`) describe what the agent is asked to do, keeping the canned `scene/` an answer rather than a hint.
