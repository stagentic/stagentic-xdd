import json
from unittest.mock import MagicMock

import pytest

from claude_session import ClaudeSession
from critic import Critic


class TestCritic:
    @pytest.fixture
    def evidence_source(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    def test_evaluation_should_build_prompt_and_delegate_to_session(self, evidence_source, tmp_path):
        working_dir = tmp_path / "workspace"
        session_spy = MagicMock(spec=ClaudeSession)
        session_spy.run.return_value = (
            '[{"characteristic": "a characteristic", "status": "PASS"}]'
        )

        Critic(session=session_spy).evaluate(
            evidence_source=evidence_source,
            working_dir=working_dir,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

        session_spy.run.assert_called_once_with(
            prompt=(
                f"Transcript: {evidence_source}\n"
                f"Workspace: {working_dir}\n\n"
                "Evaluate each of the following characteristics against the transcript and workspace.\n"
                "Respond with only a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
                "Characteristics:\n- a characteristic"
            ),
            working_dir=working_dir,
            transcript_path=working_dir / "critique.md",
        )

    def test_evaluation_should_include_distinct_evidence_source_in_prompt(self, tmp_path):
        evidence_source = tmp_path / "different_transcript.md"
        evidence_source.write_text("anything")
        session_spy = MagicMock(spec=ClaudeSession)
        session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

        Critic(session=session_spy).evaluate(
            evidence_source=evidence_source,
            working_dir=tmp_path,
            should=[{"characteristic": "any", "failure": "n/a"}],
        )

        assert str(evidence_source) in session_spy.run.call_args.kwargs["prompt"]

    def test_evaluation_should_pass_distinct_working_dir_to_session(self, evidence_source, tmp_path):
        working_dir = tmp_path / "different_workspace"
        session_spy = MagicMock(spec=ClaudeSession)
        session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

        Critic(session=session_spy).evaluate(
            evidence_source=evidence_source,
            working_dir=working_dir,
            should=[{"characteristic": "any", "failure": "n/a"}],
        )

        prompt = session_spy.run.call_args.kwargs["prompt"]
        assert str(working_dir) in prompt
        assert session_spy.run.call_args.kwargs["working_dir"] == working_dir
        assert session_spy.run.call_args.kwargs["transcript_path"] == working_dir / "critique.md"

    def test_evaluation_should_fail_when_a_characteristic_fails(self, evidence_source, tmp_path):
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = '[{"characteristic": "my characteristic", "status": "FAIL"}]'

        with pytest.raises(AssertionError) as excinfo:
            Critic(session=session_stub).evaluate(
                evidence_source=evidence_source,
                working_dir=tmp_path,
                should=[{"characteristic": "my characteristic", "failure": "my failure message"}],
            )

        assert "my characteristic" in str(excinfo.value)
        assert "my failure message" in str(excinfo.value)

    def test_failure_message_should_list_every_failed_row(self, evidence_source, tmp_path):
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = (
            '[{"characteristic": "first", "status": "FAIL"},'
            ' {"characteristic": "middle", "status": "PASS"},'
            ' {"characteristic": "third", "status": "FAIL"}]'
        )

        with pytest.raises(AssertionError) as excinfo:
            Critic(session=session_stub).evaluate(
                evidence_source=evidence_source,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "first", "failure": "first failure"},
                    {"characteristic": "middle", "failure": "middle failure"},
                    {"characteristic": "third", "failure": "third failure"},
                ],
            )

        message = str(excinfo.value)
        assert "first" in message and "first failure" in message
        assert "middle" not in message and "middle failure" not in message
        assert "third" in message and "third failure" in message

    def test_evaluation_should_tolerate_prose_before_json(self, evidence_source, tmp_path):
        prose_then_json = (
            'Based on my evaluation:\n\n'
            '[{"characteristic": "a characteristic", "status": "PASS"}]'
        )
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = prose_then_json

        Critic(session=session_stub).evaluate(
            evidence_source=evidence_source,
            working_dir=tmp_path,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

    def test_evaluation_should_tolerate_a_fenced_json(self, evidence_source, tmp_path):
        markdown = '```json\n[{"characteristic": "a characteristic", "status": "PASS"}]\n```\n'
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = markdown

        Critic(session=session_stub).evaluate(
            evidence_source=evidence_source,
            working_dir=tmp_path,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

    def test_evaluation_should_tolerate_prose_before_a_fenced_json(self, evidence_source, tmp_path):
        prose_then_fence = (
            'Based on the transcript:\n\n'
            '```json\n[{"characteristic": "a characteristic", "status": "PASS"}]\n```\n'
        )
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = prose_then_fence

        Critic(session=session_stub).evaluate(
            evidence_source=evidence_source,
            working_dir=tmp_path,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

    def test_evaluation_should_raise_ValueError_with_cause_when_response_is_not_valid_json(self, evidence_source, tmp_path):
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = "not valid json."

        with pytest.raises(ValueError, match="not valid JSON") as excinfo:
            Critic(session=session_stub).evaluate(
                evidence_source=evidence_source,
                working_dir=tmp_path,
                should=[{"characteristic": "a characteristic", "failure": "my failure"}],
            )

        assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)

    def test_evaluation_should_raise_ValueError_when_a_characteristic_is_missing_from_the_response(self, evidence_source, tmp_path):
        session_stub = MagicMock(spec=ClaudeSession)
        session_stub.run.return_value = '[{"characteristic": "a characteristic", "status": "PASS"}]'

        with pytest.raises(ValueError, match="unaccounted"):
            Critic(session=session_stub).evaluate(
                evidence_source=evidence_source,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "a characteristic", "failure": "x"},
                    {"characteristic": "another characteristic", "failure": "y"},
                ],
            )
