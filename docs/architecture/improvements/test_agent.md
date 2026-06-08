# Improvements: test_agent.py

Known improvements for `play/tests/test_agent.py`, measured against
`docs/architecture/conventions/test-conventions.md` and the reference standard
`tests/test_critic.py`. Mutation coverage is already clean (18 mutants, 0
survivors), so these are convention divergences, not coverage gaps.

## a — Inline assertions bypass PyHamcrest

Lines 43 and 65 use bare `assert agent.transcript == transcript_path`. The
*Assertion vocabulary* convention (ADR 0011) routes inline assertions through
`assert_that(actual, <matcher>)`; `test_critic.py` uses
`assert_that(str(excinfo.value), equal_to(...))`.

- Pro: one assertion vocabulary across inline and call assertions; matches the
  reference.
- Con: bare `==` reads clearly for a single Path equality, and this is the only
  inline-assert form in the file.

## b — Whole-story name names the method, not a behavioural subject

`test_perform_should_call_session_...` leads with `perform`, the method called.
*Test naming* asks the name to read as a behavioural claim about the subject,
"not as a description of the method called" — the reference uses `evaluation`,
not `evaluate`. Candidate: `test_agent_should_call_session_with_the_task_and_expose_the_transcript`.

- Trade-off: "performance" is an awkward nominalisation of `perform`; `agent` is
  the natural substitute subject, but `perform` is undeniably descriptive.

## c — Two tests float at the top of `TestAgent`, ungrouped

The whole-story and `test_transcript_location_should_be_available_after_perform`
sit loose; only `TestCallsSession` is a phase class. The reference frames the
file with outcome classes plus phase classes plus a trailing `TestErrors`.

- Note: `Agent.perform` has no guard, no pass/fail split, and never raises — far
  less to frame than `Critic`. The transcript-location property could move into
  a phase class (e.g. `TestExposesTranscript`), with the whole-story leading
  `TestAgent`.
- Trade-off: full class scaffolding may over-structure a three-line method.

## d — `test_transcript_location_...` juggles `str` then `Path`

The test sets `working_dir = "/other/dir"` (a `str`), then wraps `Path(working_dir)`
at both the call and the assertion. The other tests pass a `Path` directly. It
does correctly serve as the per-property companion to the whole-story's
transcript assertion (a different value, `/other/dir` vs `/work`).

- Pro of changing: drop the str/Path juggling; pass a `Path`.

## e — Redundant parentheses

`name=(_TASK_NAME)` and `task=(_TASK_NAME)` (lines 32, 39, 40) wrap a bare name
in parentheses. Cosmetic.

## Already conforming (do not regress)

- *Per-property layout, relevant-at-top*: `TestCallsSession` puts the relevant
  slot on top with `prompt=ANY, working_dir=ANY` bundled below.
- *Whole-story kwarg order*: follows `session.run`'s signature order (exempt from
  relevance-first).
- *Value-flow ≥2 cases*: prompt, working_dir, and transcript_path each get a
  second example via a per-property test using a value different from the
  whole-story — the companion rule is satisfied without parametrising.
- The two prompt tests are distinct: `..._from_task_file` pins prompt-content
  flow; `..._from_the_named_task` pins task-name selection.
