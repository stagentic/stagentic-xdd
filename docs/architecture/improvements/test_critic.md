# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`, accumulated
during the refactoring pass.

## TestFails should lead the file

The whole-story test (`test_evaluation_should_call_session_and_raise_for_failed_characteristics`)
lives in `TestFails`, because Critic's distinguishing behaviour is raising. Per
`test-conventions.md` §"Whole-story tests" → *Position*: "The outcome class
containing the whole-story leads. ... TestFails when the subject's job is to raise
(e.g. Critic asserting)..."

Currently `TestPasses` leads; `TestFails` follows. Target order: `TestFails` →
phase classes (`TestBuildsPrompt`, `TestCallsSession`, `TestParsesResponse`) →
`TestPasses` (trailing outcome that frames the file) → `TestErrors`.

## TestParsesResponse needs `does_not_raise()`

`test_evaluation_should_tolerate_wrapped_json` carries no positive assertion —
its sole claim is no-raise tolerance across the three wrapping forms. Per
`test-conventions.md` §"Explicit no-raise via `does_not_raise`": "When a test
asserts that the subject does not raise ... wrap the call in `does_not_raise()`."

Wrap the call inside the parametrised method body.
