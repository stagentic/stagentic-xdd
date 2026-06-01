# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`, accumulated
during the refactoring pass.

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
