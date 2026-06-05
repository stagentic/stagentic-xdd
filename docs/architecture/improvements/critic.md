# Improvements: critic.py

Known improvement for `play/src/critic.py`.

## Module-level smell: many private helpers

The module currently has 20+ private functions outside the `Critic`
class. The `Critic` class itself is small — just `__init__` and
`evaluate` — but the surrounding helpers carry the bulk of the
behaviour. Symptoms:

- Reading top-to-bottom takes a long scroll past helpers that aren't
  conceptually grouped.
- Some helpers (notably `_raise_if`) are pure utilities that could
  serve other modules.
- The file mixes responsibilities — see
  [Responsibilities mixed into the module](#responsibilities-mixed-into-the-module)
  below.

### Responsibilities mixed into the module

`Critic.evaluate` is the only behaviour that is arguably Critic's own.
The surrounding module-level helpers carry six further responsibilities:

- **Orchestration** (`Critic.evaluate`): sequence the steps — run the
  session, parse the response, validate, assert — and hold the
  empty-scorecard precondition.

- **Prompt construction** (`_prompt_for`): build the LLM instruction
  from `evidence_source`, `working_dir`, and `should`.

- **Response unwrapping** (`_unwrap_json_response`,
  `_remove_content_before_json`, `_start_of_json`, `_is_scorecard`,
  `_remove_content_after_json`): strip prose and fences around the JSON
  to locate the scorecard array.

- **Response parsing** (`_rows_from`, `_rows_unless`, `_malformed`,
  `_formatted_malformed`, `_formatted_malformed_row`, `_REQUIRED_KEYS`):
  turn the unwrapped string into rows, raising for invalid JSON or rows
  missing required keys.

- **Scorecard validation** (`_statuses_from`, `_duplicates_problem`,
  `_unaccounted_problem`, `_unexpected_problem` and their `_*_in` /
  `_*_for` / `_formatted_*` helpers, `_problems_in`, `_problems_message`):
  check the rows are coherent against `should` — no duplicates, nothing
  unaccounted, nothing unexpected.

- **Check-failure evaluation** (`_failures_in`, `_failure_message`):
  determine which characteristics did not PASS and format the failure
  list.

- **Raise utility** (`_raise_if`): raise the given error with a
  formatted message when there are items. Pure infrastructure, used by
  parsing, validation, and check-failure evaluation.

`_failure_message` is byte-identical to `auditor.py`'s `_formatted` —
the one responsibility already duplicated outside this file.
