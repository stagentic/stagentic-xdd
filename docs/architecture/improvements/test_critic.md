# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`, accumulated
during the refactoring pass.

## Bundling inconsistency in TestBuildsPrompt

`test_evaluation_should_list_characteristic_names_in_prompt` bundles
its irrelevant kwargs differently from the other per-property tests
in the class. Worth a normalised pass once the rest of the file
stabilises.
