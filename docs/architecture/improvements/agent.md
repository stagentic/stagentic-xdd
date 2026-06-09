# Improvements: agent.py

Known improvements for `play/src/agent.py`, measured against
`docs/architecture/conventions/src-conventions.md` and the reference standard
`src/critic.py`. Mutation coverage is clean (21 mutants, 0 survivors), so the
open item (**b**) is a design observation, not a coverage gap.

## a — `perform` mixes mechanism with the orchestration call (resolved)

Resolved: `_prompt_for(tasks_root, task)` extracted to module level — matching
`critic`'s `_prompt_for` and the `_X_for` suffix — and inlined into the
`session.run` call, so `perform` reads as "expose the transcript, run the
session for this task". `self.transcript = working_dir / "transcript.md"` was
left inline, as the assignment is the *exposing* of state.

## b — `self.transcript` is not established in `__init__`

`transcript` is set lazily inside `perform`, so `agent.transcript` raises
`AttributeError` until `perform` has run; a reader of `__init__` doesn't see the
attribute exists. No convention rule covers this — recorded as a design
observation.

- Trade-off: declaring it in `__init__` would mean a `| None` initial state,
  which *src-conventions* (Required vs optional) discourages. Tension either way.

## c — Trailing comma on the last `session.run` argument (resolved)

Resolved alongside **a**: the trailing comma was added to
`transcript_path=self.transcript`, matching `critic`'s multi-line calls.

## Considered — error handling (no action)

`Agent.perform` adds no chosen error handling, and by the conventions it needn't:
a missing task dir / `TASK.md` raises `FileNotFoundError` and a failing
`session.run` propagates — *test-conventions* (Don't test Python's own
enforcement) and *src-conventions* (When NOT to add a guard) both say not to
guard or test these. `critic`'s `TestErrors` exists only because an empty
scorecard would *silently* no-op; `perform` has no equivalent silent-success
path.

The one candidate, if a chosen behaviour is wanted later: an empty `TASK.md`
yields `prompt=""` and `session.run` runs with no instructions — a silent
"success" that an empty-task guard (à la the empty-scorecard `ValueError`) could
surface. That would be a new behaviour, driven test-first on its own.
