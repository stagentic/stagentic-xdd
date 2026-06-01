# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`, accumulated
during the refactoring pass.

## TestParsesResponse needs `does_not_raise()`

`test_evaluation_should_tolerate_wrapped_json` carries no positive assertion —
its sole claim is no-raise tolerance across the three wrapping forms. Per
`test-conventions.md` §"Explicit no-raise via `does_not_raise`": "When a test
asserts that the subject does not raise ... wrap the call in `does_not_raise()`."

Wrap the call inside the parametrised method body.
