# Improvements: critic.py

Known improvements for `play/src/critic.py`.

## Extract the JSON parsing

`evaluate` still owns finding and decoding the scorecard JSON in the model's
reply — `_json_text_in` (with its chisels `_remove_content_before_json`,
`_start_of_json`, `_is_scorecard`, `_remove_content_after_json`) and
`_decoded_from`. That is a cohesive responsibility — "locate and decode the
scorecard JSON" — and the bulk of what remains in the module.

Extracting it to its own module would leave `evaluate` reading as named steps at
one level: prompt → parse → validate (`ScorecardResults.from_`) → assess
failures. The parser's irreducible input is the raw response string; its output
is `maybe_results`.
