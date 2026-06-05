# Improvements: critic.py

Known improvement for `play/src/critic.py`.

## Module-level smell: many private helpers

The module currently has 20+ private functions outside the `Critic`
class. The `Critic` class itself is small — just `__init__` and
`evaluate` — but the surrounding helpers carry the bulk of the
behaviour. Symptoms:

- Reading top-to-bottom takes a long scroll past helpers that aren't
  conceptually grouped.
- Some helpers are pure utilities that could serve other modules — the
  former `_raise_if` proved the point, now extracted to its own module
  (`raise_if.py`).
- The file mixes responsibilities — see
  [Responsibilities mixed into the module](#responsibilities-mixed-into-the-module)
  below.

### Responsibilities mixed into the module

`Critic.evaluate` is the only behaviour that is arguably Critic's own.
The surrounding module-level helpers carry six further responsibilities
(two — the raise utility and check-failure evaluation — now extracted):

- **Orchestration** (`Critic.evaluate`): sequence the steps — run the
  session, parse the response, validate, assert — and hold the
  empty-scorecard precondition.

- **Prompt construction** (`_prompt_for`): build the LLM instruction
  from `evidence_source`, `working_dir`, and `should`.

- **Response unwrapping** (`_json_text_in`,
  `_remove_content_before_json`, `_start_of_json`, `_is_scorecard`,
  `_remove_content_after_json`): strip prose and fences around the JSON
  to locate the scorecard array.

- **Response parsing** (`_decoded_from`, `_results_unless`,
  `_invalid_scorecard`, `_formatted_invalid_scorecard_rows`,
  `_formatted_invalid_scorecard_row`, `_REQUIRED_KEYS`): decode the JSON
  text into `maybe_results` — the decoded, not-yet-validated candidate
  results — raising `ValueError` for invalid JSON, then reject any result
  missing the required keys.

- **Scorecard validation** (`_duplicates_problem`, `_unaccounted_problem`,
  `_unexpected_problem` and their `_*_in` / `_*_for` / `_formatted_*` helpers,
  `_problems_in`, `_problems_message`): check the results are coherent against
  `should` — no duplicates, nothing unaccounted, nothing unexpected. Each
  check reads the `results` directly.

#### Extraction complete

- **Check-failure evaluation** (`_failures_in`): determine which
  characteristics did not PASS, building its own characteristic→status lookup
  from the `results` for the one check that needs the status value. Formatting
  the failure list has moved out to `scorecard.formatted_failures_for`.

- **Raise utility** (was `_raise_if`): raise the given error with a
  formatted message when there are items. Pure infrastructure — now
  `play/src/raise_if.py`, shared by both evaluators (Critic's parsing,
  validation, and check-failure raises; Auditor's check-failure raise).

#### The carrier

`ScorecardResults` (`play/src/scorecard_results.py`) is a dumb dataclass holding
`provided_should` and `provided_rows`. `evaluate` constructs it from values
computed outside, and the validation checks read its `provided_rows`. It is the
seam the remaining scorecard responsibilities move onto: next it gains a
`results` field built from the decoded `maybe_results`, and `provided_rows` is
deleted at integration.

## Extraction strategy

Reduce the module to its sole responsibility — orchestration — by moving the
scorecard concerns onto `ScorecardResults`, the carrier that has emerged (see
above). The transport/format steps stay in `critic`: `evaluate` unwraps the
response to JSON text (`_json_text_in`) and decodes it (`_decoded_from`) into
`maybe_results` — the decoded, not-yet-validated candidate results. The carrier
receives `maybe_results` and constructs its own `results`.

The remaining moves, in order:

1. **The carrier builds and validates `results` from `maybe_results`.** Through
   a `from_*` factory taking `(should, maybe_results)`, the required-keys check
   (`_invalid_scorecard`) moves in first, then the coherence checks (duplicates,
   unaccounted, unexpected). A constructed `ScorecardResults` either exposes
   valid `results` or raises `ValueError`. `provided_rows` is deleted once
   `evaluate` uses the new path.
2. **Prompt construction** (independent of the rest; last only because it is
   first in `evaluate`'s call order).

Principles:

- **Decode stays out; validity moves in.** Unwrapping and JSON decoding are
  transport/format concerns — "is this even JSON?" — and stay in `critic`. The
  carrier owns the domain question — "are these decoded results a valid
  scorecard?" — so it receives `maybe_results` (already a Python structure) and
  never touches strings. Its irreducible input is `should` and `maybe_results`.

- **Justify extraction by clarity, not reuse.** Each responsibility moves out
  so `evaluate` reads as named steps at a single level of abstraction — worth
  doing even when there is only one caller. Cohesion sets the granularity: stop
  at a nameable responsibility, never split finer.

- **Let further types emerge empirically.** `ScorecardResults` earned its place
  once the `should`-and-results clump was visible. Apply the same restraint to
  the next candidate — `ScorecardEntry` (below) — introducing it only when its
  clump creates friction.

Orchestration is what remains once the moves land — the module's sole
responsibility.

## Next step

Strategy move 1 — `ScorecardResults` builds its `results` from `maybe_results`
— begins with this test in `play/tests/test_scorecard_results.py`:

```python
from scorecard_results import ScorecardResults


class TestScorecardResults:
    def test_from_exposes_the_results(self, dummy_scorecard):
        maybe_results = [{"characteristic": "captures input", "status": "PASS"}]

        scorecard = ScorecardResults.from_(maybe_results=maybe_results, should=dummy_scorecard)

        assert scorecard.results == maybe_results
```

- Red: `AttributeError` — no `from_` classmethod.
- Minimal green: add a `results` field and a `from_` classmethod that passes
  `maybe_results` straight to `results`. `provided_rows` keeps a default so
  `critic`'s current construction stays green until integration.
- Next test (a `maybe_results` entry missing a required key → `ValueError`)
  triangulates `_invalid_scorecard` into the factory.

## Extraction approach

When a clump of arguments recurs across several helpers and the decision is
made to fold it into a type, grow that type with expand-contract so every
step stays green. `ScorecardResults` — holding `should` and the `results`
validated from `maybe_results` — is the example here, but the recipe is general
to this pattern.

1. **Expand into a dumb carrier.** Introduce the type as a dataclass whose
   fields hold exactly the values currently passed separately — still
   computed *outside* and handed in. Name them to mark that origin (e.g.
   `provided_should`, `provided_rows`). Pass the type where the clump
   went. Nothing new is computed yet; this step is pure consolidation and
   changes no behaviour.

2. **Migrate the computation inward, one value at a time.** For each value
   the type could *derive*, TDD a member that computes it inside the type,
   expressed in terms of the type's *other members* — not the `provided_*`
   fields. Repoint the call sites at the computed member, then delete the
   now-unused `provided_*` field. One value per cycle, green throughout.

3. **Contract to the irreducible inputs.** Once every derivable value
   computes internally, the constructor shrinks to only what can't be
   derived — for `ScorecardResults`, `should` and `maybe_results`. The
   scaffold is gone.

Why it holds together:

- The type earns its responsibilities incrementally — it begins as safe
  consolidation, then absorbs one computation at a time, so no step is a
  big-bang swap.
- Computing each member from *sibling members* rather than the scaffold
  fields keeps the migrations order-independent: a value can move inward
  before or after the one it depends on, because it reads the still-
  delegating member, not the raw provided value.
- A value whose computation can raise, or that shifts *when* work happens
  (e.g. parsing that now runs on member access), needs its contract pinned
  by the existing tests at the step that moves it.

## The emergent `ScorecardEntry`

The failure-formatter consolidation kept `verify` out of `scorecard.py` by
projecting in the caller: `auditor.py`'s `_entries_from` maps its failed rows
down to `{characteristic, failure}` before handing them to
`formatted_failures_for`.

That `{characteristic, failure}` shape now recurs in three places — the
evidence a `ScorecardEntry` type would name:

- `Critic`'s `should` rows
- `Auditor`'s projected entries
- `formatted_failures_for`'s parameter (`list[dict[str, str]]`)

Following *let types emerge empirically* (above), it is not introduced yet.
When it is, the parameter becomes `list[ScorecardEntry]`, `Critic`'s `should`
produces it, and `Auditor`'s projection constructs it. Auditor adapting at its
boundary — rather than the formatter accepting verify-bearing rows via
subtyping — is what keeps the scorecard module free of `verify`.

### When it becomes compelling

Not yet — the bare dicts cost nothing while they merely flow through. The
signal is friction they can't carry:

- a change that must touch all three sites together
- a key-name slip a type would have caught
- the arrival of `ScorecardResults` (from the extraction strategy above)
  wanting a typed entry to sit on

That last trigger is why this note lives here: breaking up `critic.py` may be
what makes `ScorecardEntry` compelling.
