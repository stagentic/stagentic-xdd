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

Once you see it fail, propose the change that best implements the code that makes it pass. Make sure it is the minimum required to make the test pass (and not break any other tests). Prefer a new chisel (see critic.py) over modifying an existing one (unless it really is best to modify an existing one).

Chisels should be in _SEQUENCE in the correct order for the work it must do. Methods should be added to critic.py in call order (so, in this case — in the order they appear in the _SEQUENCE).

## Multi-fence cases

### `code-block-before-fenced-json-with-bracket-in-string`

Adversarial variant of `code-block-before-fenced-json`.

**Case:** `code-block-before-fenced-json-with-bracket-in-string`

**Target test:** `test_evaluation_should_tolerate_special_characters_inside_response_strings`

**Example:**
````python
case(
    "code-block-before-fenced-json-with-bracket-in-string",
    'Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```json\n[{"characteristic": "any [example]", "status": "PASS"}]\n```',
    "any [example]",
),
````

**Recommendation:** Include — motivates a chisel-pipeline fix.

**Context (for `code-block-before-fenced-json`):** committed earlier this session, it passes incidentally because the JSON's `[` is rightmost in the leftover text after fence-handling. This variant adds `[example]` inside a JSON string value — now *that* `[` is the rightmost, defeating the recovery.

### `code-block-before-unhinted-fenced-json-with-bracket-in-string`

Follow-up to `code-block-before-fenced-json-with-bracket-in-string` once that case is green.

**Case:** `code-block-before-unhinted-fenced-json-with-bracket-in-string`

**Target test:** `test_evaluation_should_tolerate_special_characters_inside_response_strings`

**Example:**
````python
case(
    "code-block-before-unhinted-fenced-json-with-bracket-in-string",
    'Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```\n[{"characteristic": "any [example]", "status": "PASS"}]\n```',
    "any [example]",
),
````

**Recommendation:** Include — exposes the no-language-hint variant left uncovered by a fix that anchors on `` ```json ``.

**Context (for `code-block-before-fenced-json-with-bracket-in-string`):** the prior variant is fixed by anchoring on the `json`-hinted fence. This variant drops the hint, so anchoring falls through and the same `[example]` ambiguity resurfaces.

### `code-block-after-fenced-json`

A code block in the narrative after the JSON fence.

**Case:** `code-block-after-fenced-json`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "code-block-after-fenced-json",
    '```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nFor reference, the source:\n\n```python\nprint("hello")\n```'
),
````

**Recommendation:** Include — the fence-anchor chisels lock onto the python closer at the end; basic case fails without needing brackets in strings.

### `code-block-after-fenced-json-with-bracket-in-string`

Symmetric pair to `code-block-before-fenced-json-with-bracket-in-string`.

**Case:** `code-block-after-fenced-json-with-bracket-in-string`

**Target test:** `test_evaluation_should_tolerate_special_characters_inside_response_strings`

**Example:**
````python
case(
    "code-block-after-fenced-json-with-bracket-in-string",
    '```json\n[{"characteristic": "any [example]", "status": "PASS"}]\n```\n\nFor reference, the source:\n\n```python\nprint("hello")\n```',
    "any [example]",
),
````

**Recommendation:** Exclude pre-fix; reconsider post-fix as a robustness check.

**Context (for `code-block-after-fenced-json`):** the basic after-variant already fails outright, so the bracket-in-string variant is redundant for motivating a fix.

### `code-blocks-around-fenced-json`

Natural completion of the before/after pair.

**Case:** `code-blocks-around-fenced-json`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "code-blocks-around-fenced-json",
    'Setup:\n\n```python\nx = 1\n```\n\nResult:\n\n```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nFor reference:\n\n```python\nprint(x)\n```'
),
````

**Recommendation:** Include — same failure mode as the after-variant; completes the before/after/around triple.

## Prose-after cases

### `prose-after-non-fenced-json`

A bare JSON followed by prose.

**Case:** `prose-after-non-fenced-json`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "prose-after-non-fenced-json",
    '[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.'
),
````

**Recommendation:** Include — the chisels handle prose-before-bracket but not prose-after-bracket. Fix likely adds a `_remove_prose_after_bracket` chisel.

### `prose-after-non-fenced-json-with-bracket-in-prose`

Adversarial variant of `prose-after-non-fenced-json`.

**Case:** `prose-after-non-fenced-json-with-bracket-in-prose`

**Target test:** `test_evaluation_should_tolerate_wrapped_json` (the `[note]` is in the trailing prose, not in the characteristic name).

**Example:**
````python
case(
    "prose-after-non-fenced-json-with-bracket-in-prose",
    '[{"characteristic": "any", "status": "PASS"}]\n\nSee [note] for details.'
),
````

**Recommendation:** Exclude pre-fix; include post-fix as a robustness check.

**Context (for `prose-after-non-fenced-json`):** the basic case motivates a `_remove_prose_after_bracket` chisel; this variant has `[` in the trailing prose, defeating a naive `rfind`-based fix.

### `prose-around-non-fenced-json`

Prose both before and after a non-fenced JSON.

**Case:** `prose-around-non-fenced-json`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "prose-around-non-fenced-json",
    'Based on the transcript:\n\n[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.'
),
````

**Recommendation:** Exclude — redundant.

**Context (for `prose-before-json` and `prose-after-non-fenced-json`):** the prose-before path is already covered by `prose-before-json` (existing test); the prose-after path will be covered by `prose-after-non-fenced-json` (separate entry above). This combination adds nothing not already exercised.

## Fence variants

### `fence-without-language-hint`

A fence with no language hint (just ` ``` ` instead of ` ```json `).

**Case:** `fence-without-language-hint`

**Target test:** `test_evaluation_should_tolerate_wrapped_json`

**Example:**
````python
case(
    "fence-without-language-hint",
    '```\n[{"characteristic": "any", "status": "PASS"}]\n```'
),
````

**Recommendation:** Include — documents that the language hint is optional; LLMs don't always emit it.

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

**Target test:** new test method in `TestErrors`, mirroring `test_evaluation_should_raise_when_response_is_not_valid_json`.

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
