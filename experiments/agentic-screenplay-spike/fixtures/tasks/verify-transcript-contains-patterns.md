**Directives:**
- Do not ask clarifying questions.

**TASK:**
- Read the transcript file at the path given above.
- For each regex pattern listed above, determine whether it matches somewhere in the transcript using case-insensitive Python regex semantics (equivalent to `re.search(pattern, text, re.IGNORECASE)`).
- Emit a markdown table:

  | Pattern | Matched (yes/no) |

  with one row per pattern, preserving the pattern text verbatim.

## On Completion

After the table, state OVERALL: PASS if every row's Matched value is yes, otherwise OVERALL: FAIL.
