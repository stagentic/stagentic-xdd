# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`. Surfaced while assessing
critic as a reference-standard candidate; not yet actioned.

## Repeated session setup

Nearly every test rebuilds `MagicMock(spec=ClaudeSession)` and sets
`.run.return_value` to a canned all-`PASS` array. A `passing_session` fixture
would remove the repetition for tests where the response is incidental
(`TestBuildsPrompt`, `TestCallsSession`). `TestFails` / `TestPasses` vary the
response deliberately and would keep building inline, so the fixture serves only
the "response doesn't matter" tests — at a small cost to their self-containment.

## Loose spy/stub vocabulary

In `TestBuildsPrompt`, `session_spy` plays both stub (canned return) and spy
(reads `call_args`). Defensible, but the naming drifts across the file. A
consistency pass would align names with the role each double actually plays.

## `dummy_characteristic` is singular but returns a list

The fixture name reads as one characteristic; it returns a list of one row.

## `TestPasses` is intentionally kept despite zero mutation coverage

`test_evaluation_should_not_raise_when_all_characteristics_pass` kills no mutant
the focused tests don't already kill (leave-one-out: 0 survivors) — the pass
path is exercised wherever a test runs `evaluate` with an all-`PASS` response.
It is kept deliberately as living documentation of the happy path. Don't remove
it on a mutation-only basis — this is an accepted redundancy, in the spirit of
ADR 0010's accepted-mutation handling.
