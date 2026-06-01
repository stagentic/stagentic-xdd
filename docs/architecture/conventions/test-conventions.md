# Test conventions

Test-shape and MagicMock conventions that should persist across refactors. A fresh contributor might be tempted to "simplify" or "improve" these patterns; this document captures why each one is the way it is.

## Test naming: `test_<subject>_should_<behaviour>`

Test methods are named `test_<subject>_should_<behaviour>` (e.g. `test_evaluation_should_not_raise_when_all_characteristics_pass`, `test_failure_message_should_list_every_failed_row`). The subject is the thing whose behaviour is being asserted (the evaluation, the failure message, the path); the behaviour describes what the subject does or does not do.

**Why:** the test name reads as a behavioural claim, not as a description of the method called or the mechanism. A reader scanning the file sees what the code *does*, not which method is invoked.

## Test order follows the production code's execution flow

Tests inside a `TestX` class are ordered to mirror the execution flow of the production method under test: precondition guards first, then the mechanism (what the method does internally), then the outcomes (happy path, then unhappy path).

**Why:** a reader walking the file in order encounters tests in the same direction the production code runs — guard checks first, then the work, then the results. The file reads as a sequence of "here's what happens next" rather than an unordered grab bag.

Whole-story tests lead their containing scope, before per-property tests — see *Whole-story tests*.

## Whole-story tests

A **whole-story test** pins *everything the subject does* — such as every call to every collaborator, in one test. Per-property tests drill into smaller specific facts the whole-story covers. The whole-story test may be written first or last (the latter allowing for the code to be built up one test at a time).

**The whole-story test shows the subject's distinguishing outcome.** When the subject's purpose is to dispatch a call to a collaborator (e.g. `ClaudeSession.run`), the whole-story shows that call going through. When the subject's purpose is to raise — to assert, to signal a failure — the whole-story shows it raising, because without the raise the test stops short of what the subject *does*. The reader sees the subject end-to-end, not just up to the work that precedes the user-facing outcome.

**Not every exact-match (`==`) test is a whole-story test.** Pinning one error message via `==` is just exact-match pinning of one aspect (see *Pin exact composed output once via `==`*); it tells the reader *the format of one error*, not *everything the subject does*.

**Term discipline:** always refer to it as a "whole-story test" (the noun phrase), not the bare adjective "a whole-story". The noun makes clear it is a kind of test, not a kind of assertion.

**Shape:** pin the composed collaborator interaction exactly via `==` / `assert_called_once_with` (see *Pin exact composed output once via `==`*). One example per property is enough in the whole-story itself — the second example for each property comes from a sibling per-property test (see companion rule below).

**Position:** the whole-story leads its containing class. For collaborator-grouping files (`TestCallsX`), the containing class is the file's lead class. For outcome-grouping files (`TestPasses`/`TestFails`/`TestErrors`), the containing class is the outcome class that captures the subject's distinguishing behaviour — `TestFails` when the subject's job is to raise (e.g. Critic asserting), or `TestPasses`/`TestSucceeds` when the subject's job is silent completion. Per-property tests within each class follow in execution-flow order (*Test order follows the production code's execution flow*).

Outcome and phase groupings can combine: outcome classes (`TestPasses`, `TestFails`) frame the file; phase classes (`TestBuildsPrompt`, `TestCallsSession`, `TestParsesResponse`) sit in between in play order; `TestErrors` trails as the exception paths. The outcome class containing the whole-story leads.

**Companion rule for per-property tests:** when a whole-story test exists, per-property tests for value-flow properties may collapse from parametrised (≥2 cases) to a single example — provided that example uses a value *different* from the whole-story's. The pair (per-property + whole-story) supplies the ≥2 examples needed for mutation coverage (see *Parametrise value-flow tests over ≥2 cases with `ids`*). If the values match, the second example evaporates.

**Don't split into per-fact tests.** When a whole-story test exists, per-property tests don't earn their place by virtue of being possible — they earn their place when value, presence, or absence alters behaviour (see *Pin exact composed output once via `==`*). Fragmenting a whole-story test into one test per fact loses the integrated narrative the whole-story conveys.

**Why:** without a whole-story test, the integrated behaviour exists only as something the reader assembles from focused tests.

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

## Pin exact composed output once via `==`

When the production code composes a value from inputs, write one assertion that pins the exact composed string or structure via `==`.

**Per-property tests** (separate methods focused on a single property) earn their place when a property's **value, presence, or absence alters behaviour** — e.g. an omitted flag that triggers a different code path. Whole-story tests embody this convention's exact-match pinning — see *Whole-story tests*.

**Why:** the exact-match documents the shape — prefix, separator, ordering, glue — that a reader would otherwise have to infer from the production source, and catches accidental drift in the composition. Per-property tests make behavioural facts explicit that a whole-story exact-match alone wouldn't surface.

## Explicit no-raise via `does_not_raise`

When a test asserts that the subject does *not* raise — typically the pass scenario where the subject completes silently — wrap the call in `does_not_raise()` from `contextlib.nullcontext`:

```python
from contextlib import nullcontext as does_not_raise

with does_not_raise():
    Critic(session=session_stub).evaluate(...)
```

The context manager does nothing at runtime — pytest would still fail the test if an exception leaked through without it. But the line reads as the assertion: the reader sees `with does_not_raise()` and knows the behavioural claim. Without it, the claim is only inferable from the absence of `pytest.raises`.

**Why:** the pass outcome is a behavioural claim in its own right, on par with the raise scenarios. Making it explicit puts the two claims on the same footing.

The alias starts in the test file; lift it to `conftest.py` when a second file needs it.

## Parametrise value-flow tests over ≥2 cases with `ids`

When a test asserts that a value passed in flows through to a destination, parametrise it over at least two cases — each labelled with an id so the case name leads the row. A single hard-coded literal could pass coincidentally if the production code hard-coded the same literal.

**Shape:** parametrise via a small `case(id, value)` helper so the id leads each row, even though `pytest.param`'s id is positionally last:

```python
def case(id, value):
    return pytest.param(value, id=id)


@pytest.mark.parametrize("agent_response", [
    case(
        "prose-before-json",
        '...',
    ),
    case(
        "code-fenced-json",
        '...',
    ),
])
```

The helper starts in the test file; lift it to `conftest.py` when a second file needs it.

**Why:** the test asserts a behaviour (the value reaches its destination), not a specific value. Two cases prove the value is general; one case proves only that one specific value works.

**When this doesn't apply:** structural assertions that don't carry a value — e.g. "no exception raised when all checks pass" or "the path is under `.claude/projects`" — are correctly exercised with a single example, because the property isn't "this value flowed through" but "this structural fact holds."

The two cases may also be split across a whole-story test and a sibling per-property test, provided the values differ — see *Whole-story tests*.

## Don't test Python's own enforcement

Tests should cover behaviour the code *chooses*, not behaviour Python provides for free. Don't write tests whose only purpose is to verify a missing required keyword argument raises `TypeError`, a wrong type raises an `AttributeError`, or similar language-level guarantees.

**Why:** by that logic every signature would need a test for its required-vs-optional status and every type hint would need a test for its enforcement. The tests would balloon to document Python rather than the code. Runtime guards the code *adds* (e.g. `if not should: raise ValueError`) DO warrant tests — those are choices.

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

## Stub callable → lambda; spy callable → `MagicMock`

When a test passes a callable as part of a data literal (e.g. inside a row dict) and the callable's only job is to return a fixed value, use a `lambda` inline — it documents the call's shape at the call site. When the test needs to interrogate the callable (assert it was called, assert its args), use `MagicMock`.

**Why:** the lambda shows the callable's signature inline in the row literal, so a reader sees how the row is wired without scanning back to a local definition. A `MagicMock` would obscure that. Conversely, when the test interrogates the call, the `unittest.mock` API is the idiomatic interrogation surface; rolling a hand-written closure spy duplicates `MagicMock`'s functionality.
