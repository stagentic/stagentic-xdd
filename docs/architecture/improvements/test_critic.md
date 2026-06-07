# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`. Surfaced while assessing
critic as a reference-standard candidate; not yet actioned.

## `dummy_characteristic` is singular but returns a list

The fixture name reads as one characteristic; it returns a list of one row.

## `TestPasses` is intentionally kept despite zero mutation coverage

`test_evaluation_should_not_raise_when_all_characteristics_pass` kills no mutant
the focused tests don't already kill (leave-one-out: 0 survivors) — the pass
path is exercised wherever a test runs `evaluate` with an all-`PASS` response.
It is kept deliberately as living documentation of the happy path. Don't remove
it on a mutation-only basis — this is an accepted redundancy, in the spirit of
ADR 0010's accepted-mutation handling.
