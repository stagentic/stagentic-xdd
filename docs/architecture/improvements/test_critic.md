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

Once you see it fail, propose the change that best implements the code that makes it pass — the minimum required to pass without breaking other tests. Unwrapping lives in `_unwrap_json_response`, which runs two ordered removal stages, `_remove_content_before_json` then `_remove_content_after_json`; most cases are handled by changing one of those locators. If a case genuinely needs a new positional step, add a stage function and place it in the tuple in call order.

## Prose-after cases

### `prose-around-json`

Prose both before and after a non-fenced JSON.

**Case:** `prose-around-json`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "prose-around-json",
    'Based on the transcript:\n\n[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.'
),
````

**Recommendation:** Exclude — redundant.

**Context (for `prose-before-json` and `prose-after-json` in `play/tests/test_critic.py`):** the prose-before path is covered by `prose-before-json`; the prose-after path is covered by `prose-after-json`. The removal stages run in sequence with no shared state: after `_remove_content_before_json` trims the leading prose, the intermediate text is byte-identical to a prose-after-only case, so `_remove_content_after_json` sees the same input it would have anyway. This combination adds nothing not already exercised.

## Fence variants

### `tilde-fence`

A markdown fence using tildes instead of backticks.

**Case:** `tilde-fence`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "tilde-fence",
    '~~~json\n[{"characteristic": "any", "status": "PASS"}]\n~~~'
),
````

**Recommendation:** Exclude — tilde fences are very rare from LLMs; supporting them adds complexity for negligible coverage.

## Special structures

### `multiple-json-arrays-in-response`

An LLM emits two separate JSON arrays in one response.

**Case:** `multiple-json-arrays-in-response`

**Target test:** new test method (the characteristics `"a"` and `"b"` don't match `dummy_characteristic`, so a custom `should` is needed).

**Example:**
````python
case(
    "multiple-json-arrays-in-response",
    '```json\n[{"characteristic": "a", "status": "PASS"}]\n```\n\n```json\n[{"characteristic": "b", "status": "FAIL"}]\n```'
),
````

**Recommendation:** Exclude — behaviour undefined; address by prompt-design rather than parser robustness.

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

### `empty-array` and `empty-array-in-fence`

An empty JSON array (the critic found nothing to evaluate, or some bug emits `[]`).

**Case:** `empty-array` / `empty-array-in-fence`

**Target test:** new test method (the empty `should` and `[]` rows don't fit either existing parametrize).

**Example:**
````python
case(
    "empty-array",
    '[]'
),

case(
    "empty-array-in-fence",
    '```json\n[]\n```'
),
````

**Recommendation:** Exclude — already correctly handled; `json.loads` returns `[]`, downstream `_unaccounted_problem` raises with a meaningful message.
