# Test conventions

MagicMock and broader test-shape conventions that should persist across refactors. A fresh contributor might be tempted to "simplify" or "improve" these patterns; this document captures why each one is the way it is.

## MagicMock interrogation forms

Spy interrogation uses one of these five forms — picked by the shape of the call being spied on and what the assertion needs to express.

**Equality on kwargs / no-spec spies:** `spy.method.assert_called_once_with(arg=expected, other=ANY)` with `unittest.mock.ANY` for don't-care slots. Pins call count, the named arg's value, and the presence of the other kwargs in a single expression.

**Predicate, or `spec=Class` directly-callable spies:** `spy.assert_called_once(); value = spy.call_args.kwargs[name]; assert <predicate>(value)`. Use when the assertion isn't equality (substring, startswith, cross-spy compare) or when the spec gotcha (see below) prevents `assert_called_once_with` from binding.

**Record-and-delegate:** `spy = MagicMock(side_effect=stub_callable)`. When the spy needs to record calls AND return a real-shape result, `side_effect` invokes the stub with the same args and returns its result; `spy.call_args` records the call as usual.

**Multi-call:** `assert spy.call_count == N; first, second = spy.call_args_list; assert first.kwargs[name] != second.kwargs[name]`. Pins the exact call count and inspects each call independently — no reliance on "the last call's value."

**Pure stub (no interrogation):** `MagicMock(return_value=value)`. When the spy's only job is to return a value, not to record calls.

**Why:** the `unittest.mock` toolkit has a native idiom for each shape. Picking the right form pins call count, args, and intent in one expression rather than inferring count from list-length or splitting count and args across separate assertions.

## `spec=Class` vs `spec=Class()` for directly-callable spies

When the spy stands in for a class whose *methods* you call (`session_spy.run(...)`), use `MagicMock(spec=ClassName)` — the class form. When the spy is *invoked directly* as `spy(...)` (because the underlying type is itself a callable, e.g. `ClaudeCli.__call__`), use `MagicMock(spec=ClassName())` — an instance.

**Why:** with `spec=Class`, MagicMock binds `mock(...)` to `Class.__init__`'s signature — because calling a class is constructing an instance. If the real call site invokes `__call__` (different signature), `assert_called_once_with` runs both expected and actual through `_call_matcher`, which fails to bind both as `TypeError`, and the assertion fails even when the args visibly match. `spec=Class()` introspects the instance, binding `mock(...)` to the instance's `__call__` method instead.

**Trigger to revisit:** if a new spy target is itself directly callable (has `__call__`) and the assertion uses `assert_called_once_with`, prefer the instance spec form.

## Parametrise value-flow tests over ≥2 cases with `ids`

When a test asserts that a value passed in flows through to a destination, parametrise it over at least two cases with `ids=["case-a", "case-b"]`. A single hard-coded literal could pass coincidentally if the production code hard-coded the same literal.

**Why:** the test asserts a behaviour (the value reaches its destination), not a specific value. Two cases prove the value is general; one case proves only that one specific value works.

**When this doesn't apply:** structural assertions that don't carry a value — e.g. "no exception raised when all checks pass" or "the path is under `.claude/projects`" — are correctly exercised with a single example, because the property isn't "this value flowed through" but "this structural fact holds."

The two cases may also be split across a whole-story test and a sibling per-property test, provided the values differ — see *Whole-story tests*.

## Pin exact composed output once via `==`

When the production code composes a value from inputs, write one assertion that pins the exact composed string or structure via `==`.

**Per-property tests** (separate methods focused on a single property) earn their place when a property's **value, presence, or absence alters behaviour** — e.g. an omitted flag that triggers a different code path. Whole-story tests embody this convention's exact-match pinning — see *Whole-story tests*.

**Why:** the exact-match documents the shape — prefix, separator, ordering, glue — that a reader would otherwise have to infer from the production source, and catches accidental drift in the composition. Per-property tests make behavioural facts explicit that a whole-story exact-match alone wouldn't surface.

## Stub callable → lambda; spy callable → `MagicMock`

When a test passes a callable as part of a data literal (e.g. inside a row dict) and the callable's only job is to return a fixed value, use a `lambda` inline — it documents the call's shape at the call site. When the test needs to interrogate the callable (assert it was called, assert its args), use `MagicMock`.

**Why:** the lambda shows the callable's signature inline in the row literal, so a reader sees how the row is wired without scanning back to a local definition. A `MagicMock` would obscure that. Conversely, when the test interrogates the call, the `unittest.mock` API is the idiomatic interrogation surface; rolling a hand-written closure spy duplicates `MagicMock`'s functionality.

## Don't test Python's own enforcement

Tests should cover behaviour the code *chooses*, not behaviour Python provides for free. Don't write tests whose only purpose is to verify a missing required keyword argument raises `TypeError`, a wrong type raises an `AttributeError`, or similar language-level guarantees.

**Why:** by that logic every signature would need a test for its required-vs-optional status and every type hint would need a test for its enforcement. The tests would balloon to document Python rather than the code. Runtime guards the code *adds* (e.g. `if not should: raise ValueError`) DO warrant tests — those are choices.

## Test order follows the production code's execution flow

Tests inside a `TestX` class are ordered to mirror the execution flow of the production method under test: precondition guards first, then the mechanism (what the method does internally), then the outcomes (happy path, then unhappy path).

**Why:** a reader walking the file in order encounters tests in the same direction the production code runs — guard checks first, then the work, then the results. The file reads as a sequence of "here's what happens next" rather than an unordered grab bag.

Whole-story tests lead their containing scope, before per-property tests — see *Whole-story tests*.

## Test naming: `test_<subject>_should_<behaviour>`

Test methods are named `test_<subject>_should_<behaviour>` (e.g. `test_evaluation_should_not_raise_when_all_characteristics_pass`, `test_failure_message_should_list_every_failed_row`). The subject is the thing whose behaviour is being asserted (the evaluation, the failure message, the path); the behaviour describes what the subject does or does not do.

**Why:** the test name reads as a behavioural claim, not as a description of the method called or the mechanism. A reader scanning the file sees what the code *does*, not which method is invoked.

## Whole-story tests

A **whole-story test** specifies a small behaviour in its entirety, e.g. the full series of calls to delegates, where per-property tests may assert smaller related behaviours. It conveys the integrated behaviour at a glance, while per-property tests cover each focused fact.

**Shape:** pin the composed collaborator interaction exactly via `==` / `assert_called_once_with` (cf. *Pin exact composed output once via `==`*). One example per property is enough in the whole-story itself — the second example for each property comes from a sibling per-property test (see companion rule below).

**Position:** at the top of the containing scope — the start of the file when collaborator groupings (`TestCallsX`) follow, or the start of `TestSucceeds` when outcome groupings (`TestSucceeds`/`TestFails`/`TestErrors`) are used. Per-property tests then follow in execution-flow order (*Test order follows the production code's execution flow*).

**Companion rule for per-property tests:** when a whole-story test exists, per-property tests for value-flow properties may collapse from parametrised (≥2 cases) to a single example — provided that example uses a value *different* from the whole-story's. The pair (per-property + whole-story) supplies the ≥2 examples needed (*Parametrise value-flow tests over ≥2 cases with `ids`*). If the values match, the second example evaporates.

**Why:** the whole-story conveys the integrated behaviour that a reader otherwise has to assemble from focused tests. Leading with it gives the reader the headline first; per-property tests then drill into specific facts the whole-story has already introduced.

## Per-fact test layout: relevant kwargs at the top

In per-fact tests, lay out multi-line kwarg blocks so the relevant slots sit at the top of each call (constructor, method call, `assert_called_once_with`). Irrelevant slots go below. Bundling adapts to the counts so the top stays focused.

**1 relevant + ≥1 irrelevant** — relevant alone on top; irrelevants bundled on a single line below:

```python
ClaudeSession(
    transcriber=transcriber_spy,      # relevant — alone on top
    claude=dummy, home=dummy,         # irrelevant — bundled below
)
```

**≥2 relevant + 1 irrelevant** — relevants bundled together on top; the lone irrelevant on its own line below:

```python
ClaudeSession(
    transcriber=transcriber_spy, home=home,   # relevant — bundled on top
    claude=dummy,                              # irrelevant — alone below
)
```

Apply the same shape at every kwarg block in the test — constructor, method call, `assert_called_once_with`. A reader's eye learns the layout once and recognises it across the test.

**Why:** what appears at the top of a kwarg block draws the reader's eye. Placing relevant data at the top signals what the test is about; bundling adapts to the counts so the top stays concise.

**Whole-story tests are exempt** — they follow production signature order. They aren't focused on one slot, so there's no "relevance-first" to express. See *Whole-story tests*.
