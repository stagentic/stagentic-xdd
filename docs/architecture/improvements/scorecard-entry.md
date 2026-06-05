# Improvements: ScorecardEntry

A `{characteristic, failure}` shape recurs across the scorecard code — the
evidence a `ScorecardEntry` type would name:

- `Critic`'s `should` rows (handed to `ScorecardResults.from_` as bare dicts)
- `Auditor`'s projected entries
- `formatted_failures_for`'s parameter (`list[dict[str, str]]`)

Following *let types emerge empirically*, it is not introduced yet. When it is,
the parameter becomes `list[ScorecardEntry]`, `Critic`'s `should` produces it,
and `Auditor`'s projection constructs it. Auditor adapting at its boundary —
rather than the formatter accepting verify-bearing rows via subtyping — is what
keeps the scorecard module free of `verify`.

## When it becomes compelling

The bare dicts cost nothing while they merely flow through. The signal is
friction they can't carry:

- a change that must touch all three sites together
- a key-name slip a type would have caught
- `ScorecardResults.from_` now takes `should` as bare dicts — the typed entry it
  could sit on has arrived, so this trigger is live rather than hypothetical
