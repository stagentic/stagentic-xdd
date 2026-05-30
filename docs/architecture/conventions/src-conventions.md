# Src conventions

Production code conventions for `play/src/` that should persist across refactors. A fresh contributor might be tempted to relax these to silence a warning or save a line; this document captures why each one is the way it is.

## Type hints on every public method parameter

Public method signatures hint every parameter with a concrete type (`Path`, `str`, `list[dict]`, `ClaudeCli`). Helpers may follow the same rule when their signature reveals contract details, but the public surface always does.

**Why:** a reader learns the contract from the signature without reading the body. `agent.py`'s `Agent.perform(self, *, task: str, working_dir: Path)` says everything about what `perform` consumes; `claude_session.py`'s constructor types its collaborators (`claude: ClaudeCli, transcriber: Transcriber, home: Path`) so the dependency shape is self-evident.

**Avoid `Any`:** if you reach for `from typing import Any`, ask whether `dict`, `list`, or a concrete type would fit. The auditor's `should` is `list[dict]`, not `list[Any]` — the latter conveys nothing the bare container doesn't.

## Required vs optional: no `| None = None` defaults for test convenience

When the production contract always supplies a value, the signature reflects that — no `= None` default, no `Path | None`. Don't relax the contract to make unit tests easier to write; update the tests to pass the value (a `tmp_path`-backed fixture is enough).

**Why:** the `| None = None` default lies about the contract. A reader sees an optional parameter and assumes the code handles `None`; in reality the only caller passing `None` is a test that didn't want to bother. Requiring the value at the signature surfaces an omitted argument at call time (Python raises `TypeError`) rather than letting `None` propagate to a callback or an internal helper.

## Runtime guards for semantic preconditions the type system can't express

Add a runtime guard (`if not should: raise ValueError("scorecard must not be empty")`) when the semantic precondition can't be expressed in the type system. An empty list satisfies `list[dict]`; only the runtime guard catches the degenerate case.

**Why:** the guard surfaces a misuse rather than letting it silently no-op. `Auditor.evaluate` with an empty `should` would otherwise return `None` and look successful; the `ValueError` says "the call had no effect — that's not what you meant."

**When NOT to add one:** Python already enforces the misuse. Missing required arguments raise `TypeError`; wrong types are caught by linters/type-checkers. Don't duplicate language-level guarantees with runtime guards (and don't write tests for them; see `test-conventions.md`).

## Helper-function parameter order mirrors the call it makes

When a helper function calls another callable, its own parameter order matches the call's argument order. `_failures_from(content, working_dir, should)` calls `row["verify"](content, working_dir)` — the `(content, working_dir)` pair sits adjacent in both signatures.

**Why:** the helper's signature documents what it forwards to the call inside. Param ordering that breaks the call's pair (e.g. `_failures_from(content, should, working_dir)` with `verify(content, working_dir)` inside) forces a reader to mentally re-pair the arguments.

## IDE warning suppression with an inline rationale comment

When the design intent overrides an IDE warning (e.g. `Auditor.evaluate` reads as "should be static" but is kept as an instance method to match `Critic.evaluate`), suppress the warning inline with a comment explaining why.

**Why:** silencing a warning without explanation leaves the next reader to re-derive the design intent. The comment (`# - to preserve consistency with Critic.evaluate`) records the rationale next to the suppression so a future reader sees both at once.

**Trigger to revisit:** if the symmetry argument no longer holds (e.g. `Critic` itself becomes static), revisit the suppression.
