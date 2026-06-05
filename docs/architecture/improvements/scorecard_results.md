# Improvements: scorecard_results.py

Known improvements for `play/src/scorecard_results.py`.

## Large-module smell

`ScorecardResults` is a small class — just the `from_` factory — wrapped in a
stack of module-level helpers that grew as critic's validation moved here. They
fall into distinct clusters:

- **The gate** — `_results_unless`, `_invalid`, `_empty`, `_invalid_rows_in`,
  `_is_missing_key_from`, `_formatted_invalid_results`, `_formatted_invalid_result`:
  reject empty results and rows missing a required key.
- **The coherence checks** — `_duplicated`, `_formatted_duplicates`,
  `_unaccounted_for`, `_unexpected`: reject a scorecard incoherent with `should`.
- **The problem collection** — `_problems_of`, `_problems_message`: gather the
  message-or-`None` finders and join them. Generic — the same shape critic used
  before the extraction, and a candidate to share rather than keep local.

Worth reviewing for grouping or extraction so `from_` reads against a few named
collaborators rather than a long tail of helpers.
