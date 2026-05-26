import pytest
from test_doubles.stubbed_claude_cli import StubbedClaudeCli

from critic import Critic

_TRANSCRIPT_PYTEST_RAN_AND_FAILED = """\
[TOOL] **Bash** `uv run pytest tests/`

```
collected 1 item

tests/test_greeting.py F                                                 [100%]

FAILED tests/test_greeting.py::test_says_hello - AssertionError: assert 0 == "hello"
1 failed in 0.01s
```
"""

_TRANSCRIPT_NO_PYTEST = """\
I reviewed the task requirements and noted what needs to be done.
"""

_PYTEST_RAN = {
    "characteristic": "Transcript shows the agent ran pytest",
    "failure": "No pytest invocation found in the transcript",
}
_PYTEST_FAILED = {
    "characteristic": "Transcript shows a FAILED pytest result",
    "failure": "No FAILED result found in the transcript",
}
_ASSERTION_ERROR = {
    "characteristic": "Transcript shows an AssertionError",
    "failure": "No AssertionError found in the transcript",
}


def _stub_pass(*characteristics):
    rows = [{"characteristic": c["characteristic"], "status": "PASS"} for c in characteristics]
    return StubbedClaudeCli(str(rows).replace("'", '"'))


def _stub_fail(*characteristics):
    rows = [{"characteristic": c["characteristic"], "status": "FAIL"} for c in characteristics]
    return StubbedClaudeCli(str(rows).replace("'", '"'))


class TestCritic:
    def test_evaluate_raises_ValueError_when_no_claude_provided(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

        with pytest.raises(ValueError):
            Critic().evaluate(
                evidence=transcript,
                working_dir=tmp_path,
                scorecard=[_PYTEST_RAN],
            )

    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_NO_PYTEST)

        with pytest.raises(AssertionError) as excinfo:
            Critic(claude=_stub_fail(_PYTEST_RAN)).evaluate(
                evidence=transcript,
                working_dir=tmp_path,
                scorecard=[_PYTEST_RAN],
            )

        assert _PYTEST_RAN["characteristic"] in str(excinfo.value)
        assert _PYTEST_RAN["failure"] in str(excinfo.value)

    def test_evaluate_returns_none_for_a_passing_scorecard(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

        Critic(claude=_stub_pass(_PYTEST_RAN)).evaluate(
            evidence=transcript,
            working_dir=tmp_path,
            scorecard=[_PYTEST_RAN],
        )

    def test_evaluate_passes_evidence_and_working_dir_to_claude(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)
        working_dir = tmp_path / "workspace"

        received = []

        def capture(prompt, **kwargs):
            received.append(prompt)
            return _stub_pass(_PYTEST_RAN)._response

        Critic(claude=capture).evaluate(
            evidence=transcript,
            working_dir=working_dir,
            scorecard=[_PYTEST_RAN],
        )

        assert str(transcript) in received[0]
        assert str(working_dir) in received[0]

    def test_evaluate_passes_working_dir_as_workspace_to_claude(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)
        working_dir = tmp_path / "workspace"

        received_kwargs = []

        def capture(prompt, **kwargs):
            received_kwargs.append(kwargs)
            return _stub_pass(_PYTEST_RAN)._response

        Critic(claude=capture).evaluate(
            evidence=transcript,
            working_dir=working_dir,
            scorecard=[_PYTEST_RAN],
        )

        assert received_kwargs[0].get("workspace") == working_dir

    def test_evaluate_handles_json_wrapped_in_markdown_code_fence(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)
        fenced = f'```json\n{_stub_pass(_PYTEST_RAN)._response}\n```\n'

        Critic(claude=StubbedClaudeCli(fenced)).evaluate(
            evidence=transcript,
            working_dir=tmp_path,
            scorecard=[_PYTEST_RAN],
        )

    def test_evaluate_raises_ValueError_when_response_is_not_valid_json(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

        with pytest.raises(ValueError, match="unaccounted"):
            Critic(claude=StubbedClaudeCli("I cannot access those files.")).evaluate(
                evidence=transcript,
                working_dir=tmp_path,
                scorecard=[_PYTEST_RAN],
            )

    def test_failure_message_lists_every_failed_row(self, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_NO_PYTEST)

        mixed_response = (
            f'[{{"characteristic": "{_PYTEST_RAN["characteristic"]}", "status": "FAIL"}},'
            f' {{"characteristic": "{_PYTEST_FAILED["characteristic"]}", "status": "PASS"}},'
            f' {{"characteristic": "{_ASSERTION_ERROR["characteristic"]}", "status": "FAIL"}}]'
        )

        with pytest.raises(AssertionError) as excinfo:
            Critic(claude=StubbedClaudeCli(mixed_response)).evaluate(
                evidence=transcript,
                working_dir=tmp_path,
                scorecard=[_PYTEST_RAN, _PYTEST_FAILED, _ASSERTION_ERROR],
            )

        message = str(excinfo.value)
        assert _PYTEST_RAN["characteristic"] in message
        assert _PYTEST_RAN["failure"] in message

        assert _PYTEST_FAILED["characteristic"] not in message
        assert _PYTEST_FAILED["failure"] not in message

        assert _ASSERTION_ERROR["characteristic"] in message
        assert _ASSERTION_ERROR["failure"] in message
