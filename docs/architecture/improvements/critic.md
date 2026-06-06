# Improvements: critic.py

Known improvements for `play/src/critic.py`.

## `_failures_in` envies the scorecard

`evaluate` calls `_failures_in(should, scorecard.results)` — passing two values
that both live inside the `ScorecardResults` it already holds. The helper reaches
into the object for the pair it needs (feature envy).

Move the logic onto `ScorecardResults` as a method (e.g. `scorecard.failures()`):
it already owns `should` and `results`, so "which characteristics didn't earn a
PASS" is naturally its responsibility. `evaluate` then reads
`raise_if(scorecard.failures(), …)` — tell-don't-ask. This also dovetails with
the deferred `ScorecardEntry` idea in `NEXT.md`.
