# Improvements: test_critic.py

Untested edge cases for `play/tests/test_critic.py`, surfaced during
the chisel-pipeline refactor. Each entry includes an assessment:
expected outcome (red/green) and a recommendation to include (pin as
a test) or exclude (with reasoning).

## Multi-fence cases

### `code-block-before-fenced-json-with-bracket-in-string`

```python
case(
    "code-block-before-fenced-json-with-bracket-in-string",
    'Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```json\n[{"characteristic": "any [example]", "status": "PASS"}]\n```'
),
```

Adversarial variant of `code-block-before-fenced-json`. The basic
case survives incidentally via `rfind("[")`; this variant defeats
the recovery by adding `[` inside a JSON string value.

**Assessment:** RED expected. **Include** — motivates a chisel-pipeline fix.

### `code-block-after-fenced-json`

```python
case(
    "code-block-after-fenced-json",
    '```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nFor reference, the source:\n\n```python\nprint("hello")\n```'
),
```

**Assessment:** RED expected. The fence-anchor chisels lock onto the
python closer at the end; basic case fails without needing brackets
in strings. **Include.**

### `code-block-after-fenced-json-with-bracket-in-string`

```python
case(
    "code-block-after-fenced-json-with-bracket-in-string",
    '```json\n[{"characteristic": "any [example]", "status": "PASS"}]\n```\n\nFor reference, the source:\n\n```python\nprint("hello")\n```'
),
```

**Assessment:** RED expected, but redundant for motivating a fix (the
basic after-variant already fails). **Exclude pre-fix; reconsider
post-fix as a robustness check.**

### `code-blocks-around-fenced-json`

```python
case(
    "code-blocks-around-fenced-json",
    'Setup:\n\n```python\nx = 1\n```\n\nResult:\n\n```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nFor reference:\n\n```python\nprint(x)\n```'
),
```

**Assessment:** RED expected. Natural completion of the before/after
pair. **Include.**

## Prose-after cases

### `prose-after-non-fenced-json`

```python
case(
    "prose-after-non-fenced-json",
    '[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.'
),
```

**Assessment:** RED expected. The chisels handle prose-before-bracket
but not prose-after-bracket. Fix likely adds a
`_remove_prose_after_bracket` chisel. **Include.**

### `prose-after-non-fenced-json-with-bracket-in-prose`

```python
case(
    "prose-after-non-fenced-json-with-bracket-in-prose",
    '[{"characteristic": "any", "status": "PASS"}]\n\nSee [note] for details.'
),
```

**Assessment:** RED expected. Adversarial variant where the trailing
prose contains `[`, defeating any naive rfind-based fix. **Exclude
pre-fix; include post-fix** as a robustness check on whatever fix
gets applied.

### `prose-around-non-fenced-json`

```python
case(
    "prose-around-non-fenced-json",
    'Based on the transcript:\n\n[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.'
),
```

**Assessment:** RED expected (for the same reason as
`prose-after-non-fenced-json`). **Exclude** — redundant with
`prose-after-non-fenced-json` for motivating the fix, and the
prose-before path is already covered by `prose-before-json`.

## Fence variants

### `fence-without-language-hint`

```python
case(
    "fence-without-language-hint",
    '```\n[{"characteristic": "any", "status": "PASS"}]\n```'
),
```

**Assessment:** GREEN expected — the opener line is just ` ``` `,
dropped by `text.split("\n", 1)[1]`; the rest behaves like
`code-fenced-json`. **Include** to document that the language hint
is optional (LLMs don't always emit it).

### `tilde-fence`

```python
case(
    "tilde-fence",
    '~~~json\n[{"characteristic": "any", "status": "PASS"}]\n~~~'
),
```

**Assessment:** RED expected — the pipeline only recognizes
triple-backticks. **Exclude** — tilde fences are very rare from LLMs;
supporting them adds complexity for negligible coverage.

## Special structures

### `multiple-json-arrays-in-response`

```python
case(
    "multiple-json-arrays-in-response",
    '```json\n[{"characteristic": "a", "status": "PASS"}]\n```\n\n```json\n[{"characteristic": "b", "status": "FAIL"}]\n```'
),
```

**Assessment:** Behaviour undefined — should we accept the first,
last, or raise? **Exclude** — out of scope; address by prompt-design
(instruct the critic to emit one array) rather than parser
robustness.

### `truncated-json`

```python
case(
    "truncated-json",
    '[{"characteristic": "any", "status": "P'
),
```

**Assessment:** RED expected, and the existing failure path is the
*correct* behaviour (`ValueError("response did not contain valid
JSON: ...")`). **Include in `TestErrors`** to pin that we fail
loudly rather than silently accept truncation — guards against
future "be liberal" changes.

### `empty-array` and `empty-array-in-fence`

```python
case(
    "empty-array",
    '[]'
),

case(
    "empty-array-in-fence",
    '```json\n[]\n```'
),
```

**Assessment:** Currently GREEN through the unwrap, then downstream
`_unaccounted_problem` raises with a meaningful message. **Exclude**
— already correctly handled, downstream error is informative.
