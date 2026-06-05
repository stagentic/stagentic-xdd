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

- **Check-failure evaluation** (`_failures_in`, `_formatted_failures`):
  determine which characteristics did not PASS and format the failure
  list.

- **Raise utility** (`_raise_if`): raise the given error with a
  formatted message when there are items. Pure infrastructure, used by
  parsing, validation, and check-failure evaluation.

`_formatted_failures` here is byte-identical to the copy in `auditor.py` —
the one responsibility already duplicated outside this file.

## Preliminary consolidation

One duplication already exists, so converge it before extracting anything.
`critic.py`'s and `auditor.py`'s failure formatters were byte-identical and
have been renamed — both — to `_formatted_failures`, so they match in name as
well as body. Converging to identical first makes the pull-up to a shared
definition mechanical rather than a judgement call.

The remaining steps fold the two into one shared home, each its own commit:

1. **TDD a `scorecard.py` module** exposing `formatted_failures_for` (a
   public cross-module export, no leading underscore). The shared thing is
   a *scorecard* concept, not a scorecard *result*: it renders scorecard
   entries (`{characteristic, failure}`), and `Auditor` — which has no result
   object, only `verify` callbacks — shares it. Both inspectors compose with
   the free function rather than inherit it; they already satisfy the
   `Inspector` Protocol structurally. The signature reconciles to the precise
   `list[dict[str, str]]`.
2. **Migrate** `critic.py` and `auditor.py` to import it and delete their
   local copies.
3. **Relax the duplicated formatting assertions** in `test_critic` and
   `test_auditor` once `test_scorecard` owns the exact format. Those tests
   also assert which rows are selected and that evaluation raises, so they
   shed the `- characteristic: failure` exact-match rather than being deleted
   wholesale.

## Extraction strategy

Reduce the module to its sole responsibility — orchestration — by moving
each of the others out, one at a time, working back through `evaluate`'s
call order:

1. Check-failure evaluation.
2. Scorecard validation.
3. Response parsing (response unwrapping folds in as its mechanism).
4. Prompt construction (independent of the rest; last only because it is
   first in call order).

Three principles guide it:

- **Work back from the consumers.** Validation and check-failure
  evaluation consume what the earlier steps produce. Extracting them
  first lets any type they need condense from a need the code has *shown*
  — both already take `(should, statuses)` — rather than from a guess
  about what parsing should emit. Starting at parsing would force that
  decision before any consumer had demonstrated it.

- **Justify extraction by clarity, not reuse.** Each responsibility moves
  out so `evaluate` reads as named steps at a single level of abstraction
  — worth doing even when there is only one caller. Cohesion sets the
  granularity: stop at a nameable responsibility, never split finer.

- **Let types emerge empirically.** Don't design a model up front.
  Extract for clarity; introduce a type only once the code has exposed
  the data clump that justifies it. The likely one here is a
  `ScorecardResult` over the rows and `should` that validation and
  check-failure both lean on — but it earns its place when that clump is
  visible, not before.

Orchestration is what remains once the four are out — the module's sole
responsibility.

## Extraction approach

When a clump of arguments recurs across several helpers and the decision is
made to fold it into a type, grow that type with expand-contract so every
step stays green. `ScorecardResult` — consolidating `should`, `statuses`,
and `rows` — is the example here, but the recipe is general to this pattern.

1. **Expand into a dumb carrier.** Introduce the type as a dataclass whose
   fields hold exactly the values currently passed separately — still
   computed *outside* and handed in. Name them to mark that origin (e.g.
   `provided_statuses`, `provided_rows`). Pass the type where the clump
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
