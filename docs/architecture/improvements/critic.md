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

- **Response unwrapping** (`_unwrap_json_response`,
  `_remove_content_before_json`, `_start_of_json`, `_is_scorecard`,
  `_remove_content_after_json`): strip prose and fences around the JSON
  to locate the scorecard array.

- **Response parsing** (`_rows_from`, `_rows_unless`, `_malformed`,
  `_formatted_malformed`, `_formatted_malformed_row`, `_REQUIRED_KEYS`):
  turn the unwrapped string into rows, raising for invalid JSON or rows
  missing required keys.

- **Scorecard validation** (`_duplicates_problem`, `_unaccounted_problem`,
  `_unexpected_problem` and their `_*_in` / `_*_for` / `_formatted_*` helpers,
  `_problems_in`, `_problems_message`): check the rows are coherent against
  `should` — no duplicates, nothing unaccounted, nothing unexpected. Each
  check reads the raw `rows` directly.

#### Extraction complete

- **Check-failure evaluation** (`_failures_in`): determine which
  characteristics did not PASS, building its own characteristic→status lookup
  from `rows` for the one check that needs the status value. Formatting the
  failure list has moved out to `scorecard.formatted_failures_for`.

- **Raise utility** (was `_raise_if`): raise the given error with a
  formatted message when there are items. Pure infrastructure — now
  `play/src/raise_if.py`, shared by both evaluators (Critic's parsing,
  validation, and check-failure raises; Auditor's check-failure raise).

#### The carrier

`ScorecardResult` (`play/src/scorecard_result.py`) is a dumb dataclass holding
`provided_should` and `provided_rows`. `evaluate` constructs it from values
computed outside, and the validation checks read its `provided_rows`. It is the
seam the remaining responsibilities move onto.

## Extraction strategy

Reduce the module to its sole responsibility — orchestration — by moving each
of the others onto `ScorecardResult`, the carrier that has emerged (see above).
The remaining moves, in order:

1. **Response parsing into the carrier** (response unwrapping folds in as its
   mechanism). `ScorecardResult` takes the raw `result` and produces `rows` —
   JSON parsing and the malformed gate run inside it, so a constructed
   `ScorecardResult` exposes well-formed rows. This shrinks the constructor
   toward `from_outcome(should, result)`.
2. **Scorecard validation onto the carrier.** The three coherence checks read
   only `should` and `rows` — both already held — so they move onto the type,
   raising `ValueError` for an incoherent scorecard.
3. **Prompt construction** (independent of the rest; last only because it is
   first in `evaluate`'s call order).

Principles:

- **Parsing leads, because the data has collapsed to `rows`.** Validation and
  check-failure both consume `rows` directly; there is no derived index between
  parsing and its consumers, and so no emitted-type to guess. The type's
  irreducible input is therefore `result` (parsed to `rows`) and `should`.
  Pulling parsing in first makes `.rows` well-formed by construction — exactly
  what the validation that follows assumes.

- **Justify extraction by clarity, not reuse.** Each responsibility moves out
  so `evaluate` reads as named steps at a single level of abstraction — worth
  doing even when there is only one caller. Cohesion sets the granularity: stop
  at a nameable responsibility, never split finer.

- **Let further types emerge empirically.** `ScorecardResult` earned its place
  once the `should`-and-`rows` clump was visible. Apply the same restraint to
  the next candidate — `ScorecardEntry` (below) — introducing it only when its
  clump creates friction.

Orchestration is what remains once the moves land — the module's sole
responsibility.

## Extraction approach

When a clump of arguments recurs across several helpers and the decision is
made to fold it into a type, grow that type with expand-contract so every
step stays green. `ScorecardResult` — holding `should` and the `rows` parsed
from `result` — is the example here, but the recipe is general to this pattern.

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
   derived — for `ScorecardResult`, the raw `result` and `should`. The
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
- the arrival of `ScorecardResult` (from the extraction strategy above)
  wanting a typed entry to sit on

That last trigger is why this note lives here: breaking up `critic.py` may be
what makes `ScorecardEntry` compelling.
