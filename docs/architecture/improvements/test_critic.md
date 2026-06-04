# Improvements: test_critic.py

Untested edge cases for `play/tests/test_critic.py`, surfaced during
the chisel-pipeline refactor.

## Working through this list

These entries are intended to be worked through one at a time. When
presenting an entry for review, use the format shown in each section
below: a narrative lead-in, the case name, the target test the case
would be added to, the example, a recommendation (include/exclude),
and — when the entry references another case — context explaining
the relationship.

If you are asked to add it to the test, add it and run the test first to see it fail.

Once you see it fail, propose the change that best implements the code that makes it pass — the minimum required to pass without breaking other tests. Unwrapping lives in `_unwrap_json_response`, which runs two ordered removal stages, `_remove_content_before_json` then `_remove_content_after_json`; most cases are handled by changing one of those locators. A locator can discriminate by content, not only by position: `_remove_content_before_json` finds the JSON start via `_start_of_json`, which prefers the array whose decoded value is scorecard-shaped (`_is_scorecard`) over the first bracket it meets. If a case genuinely needs a new positional step, add a stage function and place it in the tuple in call order.

## Special structures

### `non-evaluation-json-before-scorecard`

An LLM emits two JSON arrays of different *types*: the evaluation result
(`characteristic`/`status` rows) and some other array-of-dicts that is not an
evaluation result (e.g. a files-changed summary the model volunteered). The
non-evaluation array comes *first* and the response starts with it — so the
scorecard trails. Only the evaluation result should be selected.

**Case:** `non-evaluation-json-before-scorecard`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`.

**Example:**
````python
case(
    "non-evaluation-json-before-scorecard",
    '[{"path": "conversion.py", "added": 12}]\n\n[{"characteristic": "any", "status": "PASS"}]'
),
````

**Recommendation:** Include — goes red today. `_is_scorecard` already requires `characteristic` and `status` on every row, so a non-evaluation array trailing the scorecard is skipped; but that alone does *not* fix this layout. Because the response starts with `[`, the early `if text.startswith("["): return 0` in `_start_of_json` returns offset 0 without inspecting content — the leading non-evaluation array is taken verbatim, never reaching `_is_scorecard`. The fix is to make the leading-`[` path content-aware too: only short-circuit when the array at offset 0 is itself a scorecard, otherwise fall through to the content-aware scan, which then finds the trailing scorecard.

### `truncated-json`

A response cut off mid-JSON (e.g., token limit reached).

**Case:** `truncated-json`

**Target test:** new test method in `TestErrors`, mirroring `test_evaluation_should_raise_ValueError_with_cause_when_response_is_not_valid_json`.

**Example:**
````python
case(
    "truncated-json",
    '[{"characteristic": "any", "status": "P'
),
````

**Recommendation:** Include — pins the existing fail-loudly behaviour (`ValueError("response did not contain valid JSON: ...")`) so future "be liberal" changes can't silently start accepting truncation.

## Status interpretation

### `non-pass-status-counts-as-failure`

The rule is *anything other than `PASS` is a failure* — not *anything other
than `FAIL` is a pass*. A status the model didn't expect (a typo, or a hedge
like `MAYBE`) must count as a failure, never silently pass.

**Case:** `non-pass-status-counts-as-failure`

**Target test:** new test method in `TestFails` (needs a custom `should` and a custom assertion message, so it doesn't fit the parser-tolerance parametrize).

**Example:**
````python
def test_evaluation_should_treat_any_non_PASS_status_as_a_failure(self, dummy_path):
    session_stub = MagicMock(spec=ClaudeSession)
    session_stub.run.return_value = (
        '[{"characteristic": "clean pass", "status": "PASS"},'
        ' {"characteristic": "clean fail", "status": "FAIL"},'
        ' {"characteristic": "hedged", "status": "MAYBE"}]'
    )

    with pytest.raises(AssertionError) as excinfo:
        Critic(session=session_stub).evaluate(
            evidence_source=dummy_path, working_dir=dummy_path,
            should=[
                {"characteristic": "clean pass", "failure": "pass reason"},
                {"characteristic": "clean fail", "failure": "fail reason"},
                {"characteristic": "hedged", "failure": "hedged reason"},
            ],
        )

    assert str(excinfo.value) == (
        "- clean fail: fail reason\n"
        "- hedged: hedged reason"
    )
````

**Recommendation:** Include — goes red today: `_failures_in` flags only `status == "FAIL"`, so `MAYBE` is silently treated as a pass and `"hedged"` is absent from the message. The fix flips the test to `statuses.get(...) != "PASS"`, so any unexpected status fails closed.
