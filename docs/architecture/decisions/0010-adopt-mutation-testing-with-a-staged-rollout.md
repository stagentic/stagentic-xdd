---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0010 — Adopt mutation testing with a staged rollout

**Status:** Proposed

## Context

A passing test suite confirms the code does what the tests check — not that
the tests would *notice* if the code changed. A test can pass while pinning
nothing: an assertion that merely duplicates a collaborator's own tests, or a
behaviour pinned in only one place that a refactor could silently drop. The
recent review of `critic`'s tests surfaced exactly this.

This matters acutely for the agentic TDD work this repo exists to build. An
agent told to "use TDD" routinely writes more code than the failing test
demands — behaviour the tests never required and therefore never pin. Mutants
emerge wherever a change to the code exceeds the need described by a failing
test. The result looks test-driven but isn't: an *illusion of test-driven
code*, where code can change in material ways without a single test failing.
Every such living mutant is an opportunity for a future change to introduce a
bug the tests won't catch.

The refactoring pass (tracked in NEXT.md) brings each production file and its
tests to a reference standard. "Looks well-tested" is a judgement; we want
evidence that each test constrains the behaviour it covers. Mutation testing
supplies it: it perturbs the production code and checks whether some test
fails. A surviving mutant marks behaviour that has slipped past what the tests
truly demanded — a behaviour no test pins.

Background and motivation: Antony Marcano, "Mutants in the Machine: The AI
Illusion of Test-Driven Code" —
https://ideas.riverglide.com/mutants-in-the-machine-the-ai-illusion-of-test-driven-code-37d623642486

## Decision

Adopt mutation testing with `mutmut`, configured per file and rolled out in
three stages tied to the refactoring pass.

Tooling — mutmut 3.x:

- `source_paths` in `[tool.mutmut]` (in `play/pyproject.toml`) is the
  accumulating set of files under mutation. A file is added when it is in the process of being brought
  to standard; the config is committed only once its mutation coverage is
  acceptable. Committing a file into `source_paths` declares its coverage a
  defended baseline.
- Test selection is pinned to the fast unit lane via
  `pytest_add_cli_args_test_selection = ["-m", "not contract and not integration"]`
  — mutants must not trigger real-CLI calls.

Two universes, reached by two commands:

- **Focus one file** — `mutmut run "<file>*"` — fast feedback on the file
  under work: while bringing it to standard during the pass, and on green
  before each commit to catch implementation overreach (see stage 3).
- **Full set** — `mutmut run` — every committed file; the done-gate.
- (`mutmut results` and `mutmut show <id>` inspect survivors.)

Staged rollout:

1. **During the refactoring pass (now):** a read-only signal. Run per file,
   surface survivors, decide case by case. Not a gate — nothing fails.
2. **Once the pass is complete:** the full-set run becomes part of "done" — no
   piece of work is complete until `mutmut run` is clean (every mutant killed
   or formally accepted) across the committed `source_paths`.
3. **Thereafter, inside the TDD cycle:** on green, before each commit, a
   focused run on the file under change surfaces implementation that exceeds
   what the test demands. The response is to dial the code back to its essence
   — removing the overreach so it does only what the test requires — then
   commit and move to the next test. The pressure is on the implementation,
   not the test suite.

## Consequences

- "Well-tested" becomes measurable per file rather than a matter of judgement.
- A committed `source_paths` entry turns a later survivor into a regression
  signal — coverage that was defended has been lost.
- **Equivalence mutants** — survivors for which no failing test is derivable —
  are unavoidable. They need a mechanism to record an accepted-mutation
  decision against the specific code, so they are not re-litigated each run.
  That mechanism is unresolved; until it exists, accepted mutants are tracked
  by hand.
- mutmut 3.x materialises a `mutants/` working copy; it is gitignored.
- The full-set run grows slower as `source_paths` accumulates — acceptable for
  a done-gate, which is why the focused run exists for iteration.
- Stages 2 and 3 change what "done" means. `CLAUDE.md` ("Before any commit"
  and the test-suite guidance) and `docs/working-practices.md` will need
  updating when those stages go live — not now.
- Pinning to the fast lane means results say nothing about
  contract/integration-covered behaviour — a deliberate scope limit.

## Alternatives considered

- **No mutation testing — rely on review judgement.** The status quo. Review
  cannot reliably tell a behaviour-pinning assertion from a vacuous one; that
  is exactly what the `critic` test review surfaced.
- **Run mutation across everything at once.** Noisy, slow, and untargeted
  while files are still being brought to standard. The per-file,
  accumulate-as-you-go approach matches the pass.
- **Gate immediately, before the pass.** Making survivors fail the build now,
  while we are still learning the tool and have no equivalence-mutant handling,
  would block work on false positives.
