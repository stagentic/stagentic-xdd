# Improvements: agent.py

Known improvements for `play/src/agent.py`, measured against
`docs/architecture/conventions/src-conventions.md` and the reference standard
`src/critic.py`. Mutation coverage is clean (18 mutants, 0 survivors), so these
are convention divergences, not coverage gaps.

## a — `perform` mixes mechanism with the orchestration call

The *Orchestrator methods read at a single level of abstraction* convention asks
a public method's body to read as declarative steps, with no inline mechanism
beside the calls. `critic.evaluate` reads that way (`prompt=_prompt_for(...)`,
`candidate_scorecard_from(...)`, …). `perform` inlines the *how* of obtaining
the prompt:

    prompt = (self._tasks_root / task / "TASK.md").read_text()

Candidate: extract a `_prompt_for(tasks_root, task)` helper — matching `critic`'s
`_prompt_for` and the `_X_for` suffix — inlined into the `session.run` call, so
`perform` reads as "expose the transcript, run the session for this task".

- Pro: separates *what* (run the session for the task) from *how* (read the
  TASK.md); matches the reference.
- Con: it's a one-line helper, so it risks over-structuring a three-line method.
- Note: leave `self.transcript = working_dir / "transcript.md"` inline — `critic`
  inlines its analogous `working_dir / "critique.md"`, and here the assignment is
  the *exposing* of state, not a throwaway temp.

## b — `self.transcript` is not established in `__init__`

`transcript` is set lazily inside `perform`, so `agent.transcript` raises
`AttributeError` until `perform` has run; a reader of `__init__` doesn't see the
attribute exists. No convention rule covers this — recorded as a design
observation.

- Trade-off: declaring it in `__init__` would mean a `| None` initial state,
  which *src-conventions* (Required vs optional) discourages. Tension either way.

## c — Trailing comma on the last `session.run` argument

`self._session.run(...)`'s last argument (`transcript_path=self.transcript`)
carries no trailing comma; `critic`'s multi-line calls do. Cosmetic; folds into
**a** if that call is touched.

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
