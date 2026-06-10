---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0013 — Agents and inspectors return a Result value rather than state or exceptions

**Status:** Accepted

## Context

Two concrete needs are settled for today: `Agent.perform` must yield the
transcript path, and `Critic`/`Auditor`.`evaluate` must yield a pass/fail
verdict a test can assert on.

A consumption style was baked into the agent and inspectors. The agent
exposed `self.transcript` — state set lazily inside `perform` — and the
inspector raised `AssertionError` internally on a failing scorecard. Neither was
a value the caller received and decided what to do with.

The motivating goal is that `stagentic-play` (which `play` becomes) be usable in
three styles:

1. Traditional pytest tests with asserts.
2. In-code Given/When/Then, Screenplay-style.
3. Gherkin, delegating to the Screenplay style.

Returning values is the common substrate for all three. The traditional style
asserts directly on returns; the Screenplay style captures returns into
cross-step state (held by an actor or a shared assistant); Gherkin delegates to
Screenplay. State-retention is a Screenplay concern, so it does not belong in
the agent or inspector — `self.transcript` was that concern leaking in early.

Python has no built-in `Result`/`Either`; it is a borrowed pattern, available
only via a library or hand-rolled.

## Decision

Play's agents and inspectors return a value rather than exposing state or raising
on a domain outcome:

- `Agent.perform` returns a `Result` carrying the transcript path.
- `Critic`/`Auditor`.`evaluate` returns the **same** `Result` type — a "Verdict"
  by name, not by type. Each variant carries a **single** payload (Rust's
  `Result<T, E>` shape, where the two arms hold different types): `Success` when
  every row is PASS, carrying the passing scorecard; `Failure` when any row is
  FAIL, carrying the failed rows — which is what the matcher needs to describe the
  mismatch. The scorecard is not duplicated onto `Failure`; no caller needs it
  back out, and a single generic `value` field per variant matches `Success`'s
  shape and stays swap-compatible with `returns`.

The `Result` is a single, shared, **hand-rolled, project-owned** type:

- Not a third-party dependency, so the type in play's public API stays ours and
  is not coupled to another project's lifecycle.
- Not two domain types — one shared shape gives the Screenplay layer a uniform
  thing to capture, and is fully exercised today (the agent pins the `Success`
  side; the critic pins both `Success` and `Failure`).
- Realised as a **generic union alias** — the variants are `Success[T]` /
  `Failure[E]` (PEP 695) and `Result` is `type Result[T, E] = Success[T] |
  Failure[E]`. The type parameter lets a return annotation such as
  `evaluate(...) -> Result[ScorecardResults, list[dict[str, str]]]` keep
  `result.value` concretely typed at the call site rather than degrading to
  `object`.

Its variants are named `Success` and `Failure`, consumed the Python way:

- Assertions read the `Success`/`Failure` state through a PyHamcrest matcher: it
  discriminates the variant and reads the payload off the variant's public fields
  for its mismatch message. No extractor — success- or failure-side `unwrap` — is
  needed, because the matcher already knows which variant it holds.
- The framework's surface is the two variants, their public fields, and the
  matcher. The dataclasses support `match`/`case` for free (via
  `__match_args__`), but consuming with `match` is a *caller* convention, not part
  of the framework; whether to prefer it over `if`/`else` is a style question,
  captured in `conventions/` only if it earns its place.
- A throw is the caller's explicit choice, not a built-in — there is no default
  `unwrap`. Where a value must come out — the spec pulling the transcript from the
  agent's result to feed the inspector — extraction reads the field after
  confirming the variant.

Exceptions stay for the genuinely exceptional — no network, a missing CLI,
unparseable output, or a run cut short by a usage limit (unrecoverable within a
test run, and often outside the developer's control). `Result` carries *expected
domain outcomes* — chiefly a scorecard `Failure`. A failing scorecard is what the
spec exists to detect, so it is a verdict to assert on, not an error to throw.

Keep the surface minimal — the two variants and their public fields, plus the
matcher. Defer until a test demands them:

- extractors — a success-side `unwrap()`, a failure-side `unwrap_err()` /
  `failure()`, and `value_or(default)` / `unwrap_or_else(f)` — none are needed
  while the matcher reads fields directly;
- combinators — `.map`, `.and_then`, `.map_failure`, `.or_else` (the `returns`
  weight we are deliberately not taking on yet);
- a `Transcript` value-object or its `content` (nothing reads content off the
  object today — the spec reads the file from disk via the path);
- the `Failure` branch on the *agent* (no failure-mode test exists; the shared
  type's `Failure` is already pinned by the critic).

Drive it test-first, by **expand–contract** (parallel change) so the suite stays
green throughout: each new return is added alongside the existing path, the spec
is migrated onto it, then the old path — `self.transcript`, then the inspector's
internal raise — is removed. The arc is agent `Success` (step 1), inspector
verdict (step 2), with the spec migrations between (step 3).

## Consequences

- The agent's `self.transcript` attribute is removed, dissolving its
  attribute-outside-`__init__` design observation: no `| None` state, no IDE
  warning, no mutation survivor.
- The failing-scorecard assertion moves to the test boundary, expressed as a
  PyHamcrest matcher (ADR
  [0011](0011-adopt-pyhamcrest-for-declarative-assertions.md)). The existing
  failure formatting becomes the matcher's mismatch description — the same rich
  message, surfaced through an assert rather than an internal throw.
- One verdict matcher is reused across all three styles — the traditional
  `assert_that`, the Screenplay `should`, and Gherkin's `Then`.
- Returning instead of raising reopens the vacuous-pass footgun: a hand-written
  test can forget to assert and pass having checked nothing. This is confined to
  the traditional style by choice; the Screenplay and Gherkin layers always
  assert. Accepted as the cost of the value-returning substrate.
- The inspector contract (ADRs
  [0007](0007-structure-inner-loop-scenarios-as-a-task-chain-with-a-scorecard.md),
  [0009](0009-select-inspector-and-agent-per-run-via-pytest-cli-options.md))
  changes from raising to returning; spec scenarios assert on the verdict.
- Consistent with ADR
  [0001](0001-start-with-tdab-and-vanilla-pytest.md): this returns values from
  agents and inspectors, it does **not** adopt a BDD/Screenplay DSL. The current scenario
  stays a traditional test with asserts; the other two styles are enabled, not
  introduced.
- The new `Result` module joins `source_paths` while it is developed (ADR
  [0010](0010-adopt-mutation-testing-with-a-staged-rollout.md)); its `Success`
  and `Failure` are both pinned today — `Success` by the agent and a passing
  critic, `Failure` by a failing critic.
- A later migration to `returns` (dry-python) becomes a localized
  reimplementation behind our own type, taken only when a real combinator need
  arises.

## Inspiration

The type is hand-rolled, but the pattern is well-trodden. What we drew from each
prior implementation:

- **Rust's `Result<T, E>`** — the concept itself: a single value that is either
  success or failure, making failure explicit and assertable rather than thrown.
  Its raising `unwrap()` we note as a *possible* explicit extraction, but do not
  take by default. We also do *not* lean on EAFP to justify a throw: EAFP favours
  forgiveness over permission, which a returned-then-inspected `Result` satisfies
  just as well — a throw is a convenience, not the grain.
- **`returns` (dry-python)** — the migration target we stay swap-compatible with,
  so adopting it later is a local change. We take its support for 3.10 structural
  pattern matching and the `Success`/`Failure` naming it shares with Result4k
  (over Rust's `Ok`/`Err`). Its `value_or(default)` we leave deferred — the
  fallback case has no caller yet — along with its combinator and
  higher-kinded-type surface and its mypy plugin.
- **Result4k (Kotlin)** — the "work with the grain of the language" principle,
  which we applied *to Python* rather than copied: `match`/`case` and the absence
  of non-local lambda returns. We follow its no-auto-throw stance — no default
  `unwrap`, a throw is the caller's explicit choice — and its restraint, with
  combinators not pushed. We deliberately do *not* port `onFailure { return … }`
  (unbuildable without non-local returns) or its type-gated `get()`; a
  `recover` / `value_or` equivalent stays deferred.

## Alternatives considered

- **Two domain-named result types** (e.g. `AgentResult`, `Verdict`). Reads more
  naturally in a traditional assert, but doubles the type surface and makes the
  Screenplay layer handle two shapes. Rejected in favour of one shared `Result`,
  aligned with a future `returns` swap and uniform capture.
- **Depend on `returns` (dry-python)** — maintained and feature-rich. Rejected
  for now: far more than needed (functional combinators, a mypy plugin), and it
  leaks a third-party type into play's public API. Kept as the migration target
  behind our own type.
- **Depend on `result` (rustedpy)** — the obvious Rust-like `Ok`/`Err`.
  Rejected: explicitly unmaintained, with the repo inviting a fork.
- **Depend on `poltergeist`** — lightweight and type-safety-focused. Rejected:
  dormant since its Apr 2024 release, no Python 3.13 classifier, 2024 issues
  unanswered — the same public-API lifecycle risk as `result`, less advanced.
- **Keep raising / keep `self.transcript`** — bakes a consumption style into the
  agent or inspector and cannot serve traditional, Screenplay, and Gherkin styles from
  one substrate. Rejected.
- **Return a bare `Path` / bare failures with no wrapper** — the critic genuinely
  needs a two-arm verdict, and a bare `Path` for the agent would split the surface
  so the Screenplay layer captures two shapes instead of one. Rejected in favour of
  one shared `Result`; should an agent *domain* failure ever emerge, the carrier
  already has a home for it rather than forcing a return-type change.
