# Improvements: test_critic.py

Known improvements for `play/tests/test_critic.py`. Surfaced while assessing
critic as a reference-standard candidate; not yet actioned.

Critic's collaborators — `failure_message`, `scorecard_results`,
`scorecard_json_extraction`, `raise_if` — each have their own test files. That
ownership boundary shapes the first two items.

## Verbatim invalid-rows message re-tests collaborator-owned formatting

`test_evaluation_should_list_invalid_response_rows` asserts the exact
`"invalid rows:\n- missing 'characteristic'…"` string. That string is produced
and owned by `scorecard_results` / `scorecard_json_extraction`, which test it
directly. Critic's only behaviour here is *propagating* the `ValueError` —
asserting the full message couples `TestCritic` to wording it doesn't own.
Narrowing to `pytest.raises(ValueError)` (or a substring) drops a verbatim check
that already lives where it belongs.

## `TestFails` bundles two behaviours

`test_evaluation_should_call_session_and_raise_for_failed_characteristics`
asserts both that `run()` was called once with the full verbatim prompt *and*
that the formatted-failures message was raised — the name concedes it. Splitting
"raises with formatted failures" from prompt construction would isolate each.
But see the next item before removing the verbatim prompt assertion.

## The prompt's instruction sentences are pinned in exactly one place

`"Evaluate each…"` and `"Respond with only…"` are asserted *only* by the
verbatim block in `TestFails`. `TestBuildsPrompt` pins evidence_source,
working_dir, and the characteristic list + separator — but not those two
sentences. So narrowing `TestFails` would leave a mutation to either sentence
undetected. Decide first whether that exact wording is behaviour worth its own
test or incidental prose.

These last two pull against the first: one item wants a verbatim assertion
*removed* as redundant with collaborator tests; the other warns one verbatim
assertion is the *sole* pin for the instruction prose. Mutation testing against
`critic.py` is the cleanest way to settle which the tests actually depend on —
and the instruction-prose case is a candidate for the "accepted mutation"
mechanism if the wording turns out to be incidental.

## Repeated session setup

Nearly every test rebuilds `MagicMock(spec=ClaudeSession)` and sets
`.run.return_value` to a canned all-`PASS` array. A `passing_session` fixture
would remove the repetition for tests where the response is incidental
(`TestBuildsPrompt`, `TestCallsSession`). `TestFails` / `TestPasses` vary the
response deliberately and would keep building inline, so the fixture serves only
the "response doesn't matter" tests — at a small cost to their self-containment.

## Loose spy/stub vocabulary

In `TestBuildsPrompt`, `session_spy` plays both stub (canned return) and spy
(reads `call_args`). Defensible, but the naming drifts across the file. A
consistency pass would align names with the role each double actually plays.

## `dummy_characteristic` is singular but returns a list

The fixture name reads as one characteristic; it returns a list of one row.
