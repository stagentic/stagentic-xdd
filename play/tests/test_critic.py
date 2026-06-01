import json
from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest

from claude_session import ClaudeSession
from critic import Critic


class TestCritic:
    @pytest.fixture
    def dummy_path(self): return Path("/dummy")

    @pytest.fixture
    def dummy_characteristic(self): return [{"characteristic": "any", "failure": "n/a"}]

    class TestSucceeds:
        def test_evaluation_should_build_prompt_and_delegate_to_session(self, tmp_path):
            evidence_source = tmp_path / "transcript.md"
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

        def test_evaluation_should_include_distinct_evidence_source_in_prompt(self, dummy_path, dummy_characteristic, tmp_path):
            evidence_source = tmp_path / "different_transcript.md"
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                evidence_source=evidence_source,
                working_dir=dummy_path,
                should=dummy_characteristic,
            )

            assert str(evidence_source) in session_spy.run.call_args.kwargs["prompt"]

        def test_evaluation_should_embed_working_dir_in_prompt(self, dummy_path, dummy_characteristic, tmp_path):
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                working_dir=tmp_path / "embedded_in_prompt",
                evidence_source=dummy_path, should=dummy_characteristic,
            )

            assert str(tmp_path / "embedded_in_prompt") in session_spy.run.call_args.kwargs["prompt"]

        def test_evaluation_should_pass_working_dir_to_session(self, dummy_path, dummy_characteristic, tmp_path):
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                working_dir=tmp_path / "passed_to_session",
                evidence_source=dummy_path, should=dummy_characteristic,
            )

            session_spy.run.assert_called_once_with(
                working_dir=tmp_path / "passed_to_session",
                prompt=ANY, transcript_path=ANY,
            )

        def test_evaluation_should_derive_critique_path_from_working_dir(self, dummy_path, dummy_characteristic, tmp_path):
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                working_dir=tmp_path / "derives_critique_path",
                evidence_source=dummy_path, should=dummy_characteristic,
            )

            session_spy.run.assert_called_once_with(
                transcript_path=tmp_path / "derives_critique_path" / "critique.md",
                prompt=ANY, working_dir=ANY,
            )

        def test_evaluation_should_list_characteristic_names_in_prompt(self, dummy_path, tmp_path):
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "first thing", "status": "PASS"}, {"characteristic": "second thing", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                should=[
                    {"characteristic": "first thing", "failure": "x"},
                    {"characteristic": "second thing", "failure": "y"},
                ],
                evidence_source=dummy_path, working_dir=tmp_path,
            )

            prompt = session_spy.run.call_args.kwargs["prompt"]
            assert "- first thing\n- second thing" in prompt

        def test_evaluation_should_tolerate_prose_before_json(self, dummy_path, dummy_characteristic):
            prose_then_json = (
                'Based on my evaluation:\n\n'
                '[{"characteristic": "any", "status": "PASS"}]'
            )
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = prose_then_json

            Critic(session=session_stub).evaluate(
                evidence_source=dummy_path,
                working_dir=dummy_path,
                should=dummy_characteristic,
            )

        def test_evaluation_should_tolerate_code_fenced_json(self, dummy_path, dummy_characteristic):
            markdown = '```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n'
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = markdown

            Critic(session=session_stub).evaluate(
                evidence_source=dummy_path,
                working_dir=dummy_path,
                should=dummy_characteristic,
            )

        def test_evaluation_should_tolerate_prose_before_fenced_json(self, dummy_path, dummy_characteristic):
            prose_then_fence = (
                'Based on the transcript:\n\n'
                '```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n'
            )
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = prose_then_fence

            Critic(session=session_stub).evaluate(
                evidence_source=dummy_path,
                working_dir=dummy_path,
                should=dummy_characteristic,
            )

    class TestFails:
        def test_evaluation_should_list_every_failed_characteristic(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = (
                '[{"characteristic": "first", "status": "FAIL"},'
                ' {"characteristic": "middle", "status": "PASS"},'
                ' {"characteristic": "third", "status": "FAIL"}]'
            )

            with pytest.raises(AssertionError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "first", "failure": "first failure"},
                        {"characteristic": "middle", "failure": "middle failure"},
                        {"characteristic": "third", "failure": "third failure"},
                    ],
                )

            assert str(excinfo.value) == "- first: first failure\n- third: third failure"

    class TestErrors:
        def test_evaluation_should_raise_when_the_scorecard_is_empty(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            with pytest.raises(ValueError, match="scorecard must not be empty"):
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[],
                )

        def test_evaluation_should_raise_ValueError_with_cause_when_response_is_not_valid_json(self, dummy_path, dummy_characteristic):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = "not valid json."

            with pytest.raises(ValueError, match="not valid JSON") as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=dummy_characteristic,
                )

            assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)

        def test_evaluation_should_list_every_unaccounted_characteristic(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = '[{"characteristic": "first", "status": "PASS"}]'

            with pytest.raises(ValueError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "first", "failure": "x"},
                        {"characteristic": "second", "failure": "y"},
                        {"characteristic": "third", "failure": "z"},
                    ],
                )

            assert str(excinfo.value) == "unaccounted characteristics: second, third"
