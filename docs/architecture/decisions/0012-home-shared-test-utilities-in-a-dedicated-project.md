---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0012 — Home shared test utilities in a dedicated `test_utilities` project

**Status:** Proposed

## Context

`play/` and `spec/` are separate pytest projects, each with its own `src/`,
`tests/`, `pyproject.toml`, and mutation gate. Shared *test* helpers — not
production code, not domain-specific — have accreted and duplicated across the
test files of `play/`:

- **matchers** (`matching`, `does_not`, `contain_string`, `contains_strings`)
  — currently `play/tests/matchers.py` (ADR
  [0011](0011-adopt-pyhamcrest-for-declarative-assertions.md)).
- **`case`** — a `pytest.param` wrapper that puts the id first — defined three
  times, in two different signatures: `def case(id, *values)`
  (`test_scorecard_results.py`, `test_scorecard_json_extraction.py`) and
  `def case(id, **named_values)` (`test_raise_if.py`).
- **`does_not_raise`** — `from contextlib import nullcontext as does_not_raise`
  — repeated in three files (`test_critic.py`, `test_raise_if.py`,
  `test_critic_integration.py`).

Two problems follow. First, these helpers have no single home: they are
duplicated (and have already drifted, as the two `case` signatures show), and
nothing tests them. Second, they get **no mutation coverage**, and that gap is
structural, not incidental.

Mutation testing is part of doing the work (ADR
[0010](0010-adopt-mutation-testing-with-a-staged-rollout.md)). But mutmut
cannot mutation-test a helper that lives under `tests/`:

- mutmut only mutates files under **hardcoded** source roots — `.`, `src`,
  `source` (in `setup_source_paths`); the list is not configurable.
- Those roots determine the dotted key mutmut derives from each file's path, so
  `tests/matchers.py` is keyed `tests.matchers`.
- The tests import the helper as `matchers` (because `pytest`'s
  `pythonpath = ["src", "tests"]` puts `tests/` on the path), and mutmut records
  the covering test under that module name.
- The keys diverge — `tests.matchers` (path) vs `matchers` (import) — so every
  mutant of the helper is silently marked "no tests" and never checked.

`src/critic.py` avoids this only because `src/` *is* a recognised root: its key
`critic` matches its import. Adding a `tests/` helper to a `source_paths` list
does not help.

The forces: one home for shared test utilities, with their own tests and
mutation coverage; a single `case`; reuse across `play` and `spec`; and working
*with* mutmut's source-root convention rather than against it.

## Decision

Create **`test_utilities/`** as a peer project to `play/` and `spec/`, with its
own `src/`, `tests/`, and `pyproject.toml`.

- Shared helpers live in `test_utilities/src/` as top-level modules (e.g.
  `matchers.py`), imported as `from matchers import …`. Under the recognised
  `src/` root, mutmut keys them `matchers` — matching the import — so they are
  mutation-testable exactly like any production module.
- `test_utilities` carries its own mutation gate
  (`[tool.mutmut] source_paths = ["src/matchers.py", …]`), **permanently**.
  This retires the workaround of temporarily adding a test helper to another
  project's `source_paths`, which cannot work (see Context).
- **Wiring lands in two phases — both committed.**
  - *Phase 1 (`pythonpath`):* `play` and `spec` each add
    `"../test_utilities/src"` to their `[tool.pytest.ini_options] pythonpath`,
    sharing the helpers and getting them mutation-tested with minimal wiring.
  - *Phase 2 (standalone package):* `test_utilities` becomes a properly
    packaged, installable project (uv workspace member) that `play` and `spec`
    declare as a dependency, retiring the relative-`pythonpath` entry.

  Phase 1 is a deliberate stepping stone, not the destination — Phase 2 is
  planned, so the relative-`pythonpath` wiring does not calcify into a permanent
  hack.
- Consolidate `case` into a single signature in `test_utilities`; the call
  sites adopt it.
- Initial scope: `matchers`, `case`, `does_not_raise`. Domain-specific helpers
  stay where they are — `characteristics_for_all` and the `dummy` fixture in
  `play/`, and `spec`'s `inspector`/`agent` fixtures, `pytest_*` hooks, `_have`,
  and `_tree_diff`.

## Consequences

- Shared test utilities gain one home, their own tests, and mutation coverage —
  closing the structural gap that mutmut cannot mutate a `tests/`-located
  helper.
- Duplication goes away: one `case`, one `does_not_raise`, one `matchers`.
- Mutation config simplifies: helpers are permanent mutation targets in their
  own project, so no temporary, uncommitted `source_paths` edits during
  development.
- A third project to maintain: its own `pyproject.toml`, lockfile, lint, and
  test invocations. `COMMANDS.md` gains its commands; `CLAUDE.md` "Layout" gains
  the project; the test-conventions "lift the alias to `conftest.py`" guidance
  and the working-practices "add the file you're developing to `source_paths`"
  wording are revised to point at `test_utilities` for shared helpers.
- Phase 1's cross-project wiring is a relative `pythonpath` entry — light and a
  little unconventional, but explicitly temporary: Phase 2 replaces it with a
  packaged dependency.
- Consolidating `case` forces choosing one signature; the call sites that used
  the other form change with it.

## Alternatives considered

- **Keep `matchers` in `play/tests/` and temporarily add it to `source_paths`
  for mutation.** Rejected: mutmut's hardcoded source roots (`.`, `src`,
  `source`) mean a `tests/`-located file's mutants never map to any test ("no
  tests") — it is not achievable, not merely awkward.
- **Move `matchers` to `play/src/`.** Rejected: misfiles test-only code as
  production, pulls it into `play`'s production mutation gate, and still gives
  `spec` no clean way to reuse it.
- **Relocate `matchers` to the `play/` project root (`.`) to hit mutmut's `.`
  convention.** Rejected: a tool-driven placement at the project root, still
  `play`-only, and with no home for the helpers' own tests.
- **Put the helpers in `conftest.py`.** Partial at best: `conftest` shares
  fixtures within a single project, not across `play`/`spec`, and gives neither
  mutation coverage nor a tested home for non-fixture helpers like `matchers`
  and `case`.
