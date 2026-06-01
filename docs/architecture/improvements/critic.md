# Improvements: critic.py

Known improvements for `play/src/critic.py`, accumulated during the
refactoring pass but deferred for follow-up. Sequenced by intended
order of work: tidy each unit in place first, so the structural
extraction question (last) is re-evaluated against an already-tidy
file.

## `_formatted_malformed` density

The body is a single dense expression — nested generator + join +
repr + f-string. Hard to read. Could be broken into clearer steps or
pull the per-row formatting into a helper.

## `_strip_code_fence` clarity

Procedural-feeling string manipulation with non-obvious branches
(`if fence_start != -1` block, then a separate `if array_start > 0`
block). The two cases (code-fenced vs prose-before-array) aren't
named. Could split into `_strip_fenced_block` and
`_strip_prose_prefix` for clarity.

## Type hint precision

Most parsed-row helpers use `list[dict]` (untyped dict). Could be
`list[dict[str, str]]` for tighter contracts, or a `TypedDict` /
small dataclass for named-field access. Thread through each item
above as units are touched, rather than as a separate sweep.

## Module-level smell: many private helpers

Revisit after the items above land — a tidier file may change the
case for extraction.

The module currently has 20+ private functions outside the `Critic`
class. The `Critic` class itself is small — just `__init__` and
`evaluate` — but the surrounding helpers carry the bulk of the
behaviour. Symptoms:

- Reading top-to-bottom takes a long scroll past helpers that aren't
  conceptually grouped.
- Some helpers (notably `_raise_if`) are pure utilities that could
  serve other modules.
- The file mixes responsibilities: response parsing, problem
  detection, message formatting, and exception raising all live
  together.

### Possible extractions

- **`_raise_if`**: generic "raise on items via formatter" helper.
  Used three times in `critic.py`. Other files in `play/src/` (e.g.
  `auditor.py`, the agent/session helpers) may benefit from the same
  pattern. Candidate for a shared helper module — e.g.
  `play/src/raise_helpers.py` — once it has at least one external
  user. Review other files for the same pattern (`if X: raise Y(Z)`)
  before lifting.

- **Response parsing** (`_rows_from`, `_strip_code_fence`,
  `_rows_unless`, `_malformed`, `_formatted_malformed`,
  `_REQUIRED_KEYS`): a self-contained "extract canonical rows from
  an LLM-shaped JSON response" responsibility. Candidate for
  `play/src/agent_response.py` (or similar), imported by `Critic`.

- **Problem detection trio** (`_duplicates_problem`,
  `_unaccounted_problem`, `_unexpected_problem` and their helpers):
  candidate for a dedicated module if other classes need similar
  scorecard validation.
