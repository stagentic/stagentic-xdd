# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`, accumulated
during the refactoring pass.

## Naming consistency

Most `TestErrors` tests are
`test_evaluation_should_list_every_X_characteristic`. Outliers:

- `test_evaluation_should_raise_when_the_scorecard_is_empty` —
  different verb structure (no `list_every_X`).
- `test_evaluation_should_raise_ValueError_with_cause_when_response_is_not_valid_json` —
  long, includes the exception type in the name.
- `test_evaluation_should_report_every_validation_problem_together` —
  different verb (`report` rather than `list`).

The variation may be intentional; worth a normalised pass if consistency
reads better than the current per-test specificity.

## Fixture scoping

`dummy_path` and `dummy_characteristic` are class-level fixtures on
`TestCritic`. They could move to module level — parallel to the
`dummy` fixture in `conftest.py` — so they're accessible if other
test classes/files want them.

## Bundling inconsistency in TestBuildsPrompt

`test_evaluation_should_list_characteristic_names_in_prompt` bundles
its irrelevant kwargs differently from the other per-property tests
in the class. Worth a normalised pass once the rest of the file
stabilises.
