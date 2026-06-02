# Improvements: test_critic.py

Untested edge cases for `play/tests/test_critic.py`, surfaced during
the chisel-pipeline refactor and deferred for follow-up.

## Adversarial `code-block-before-fenced-json` with brackets in JSON strings

`code-block-before-fenced-json` (pinned at `test_critic.py:185`)
survives incidentally because the JSON's `[` happens to be the rightmost
in the leftover text after fence-handling. Add a variant where the JSON
contains brackets inside string values; the `rfind("[")` recovery in
`_remove_prose_before_bracket` would catch the in-string bracket
instead of the array's bracket.

```python
case(
    "code-block-before-fenced-json-with-bracket-in-string",
    'Here is some code:\n\n```python\nprint("hello")\n```\n\nAnd the result:\n\n```json\n[{"characteristic": "any [example]", "status": "PASS"}]\n```'
),
```

Expected outcome: red on current code.

## `code-block-after-fenced-json`

Symmetrical to the above — a code block in the narrative *after* the
JSON fence. Less likely in practice but conceptually paired.

```python
case(
    "code-block-after-fenced-json",
    '```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n\nFor reference, the source:\n\n```python\nprint("hello")\n```'
),
```

Expected outcome: trace through the chisels when adding to confirm
(the rightmost `[` in the leftover may again be the JSON's, in which
case this would survive incidentally too).

## Prose after non-fenced JSON

A bare JSON followed by prose isn't tolerated — the chisels handle
prose-before-bracket but not prose-after-bracket.

```python
case(
    "prose-after-non-fenced-json",
    '[{"characteristic": "any", "status": "PASS"}]\n\nThat completes the evaluation.'
),
```

Expected outcome: red on current code. Fix would add a
`_remove_prose_after_bracket` chisel to the pipeline.
