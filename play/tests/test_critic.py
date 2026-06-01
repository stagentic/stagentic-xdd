import json
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest

from claude_session import ClaudeSession
from critic import Critic


def case(id, value):
    return pytest.param(value, id=id)


class TestCritic:
    @pytest.fixture
    def dummy_path(self): return Path("/dummy")

    @pytest.fixture
    def dummy_characteristic(self): return [{"characteristic": "any", "failure": "n/a"}]

    class TestFails:
        def test_evaluation_should_call_session_and_raise_for_failed_characteristics(self, tmp_path):
            evidence_source = tmp_path / "transcript.md"
            working_dir = tmp_path / "workspace"
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = (
                '[{"characteristic": "alpha", "status": "FAIL"},'
                ' {"characteristic": "beta", "status": "PASS"},'
                ' {"characteristic": "gamma", "status": "FAIL"}]'
            )

            with pytest.raises(AssertionError) as excinfo:
                Critic(session=session_spy).evaluate(
                    evidence_source=evidence_source,
                    working_dir=working_dir,
                    should=[
                        {"characteristic": "alpha", "failure": "alpha reason"},
                        {"characteristic": "beta", "failure": "beta reason"},
                        {"characteristic": "gamma", "failure": "gamma reason"},
                    ],
                )

            session_spy.run.assert_called_once_with(
                prompt=(
                    f"Transcript: {evidence_source}\n"
                    f"Workspace: {working_dir}\n\n"
                    "Evaluate each of the following characteristics against the transcript and workspace.\n"
                    "Respond with only a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
                    "Characteristics:\n"
                    "- alpha\n"
                    "- beta\n"
                    "- gamma"
                ),
                working_dir=working_dir,
                transcript_path=working_dir / "critique.md",
            )
            assert str(excinfo.value) == (
                "- alpha: alpha reason\n"
                "- gamma: gamma reason"
            )

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

    class TestBuildsPrompt:
        def test_evaluation_should_include_distinct_evidence_source_in_prompt(self, dummy_path, dummy_characteristic, tmp_path):
            evidence_source = tmp_path / "different_transcript.md"
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                evidence_source=evidence_source,
                working_dir=dummy_path, should=dummy_characteristic,
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

        def test_evaluation_should_list_characteristic_names_in_prompt(self, dummy_path):
            session_spy = MagicMock(spec=ClaudeSession)
            session_spy.run.return_value = '[{"characteristic": "first thing", "status": "PASS"}, {"characteristic": "second thing", "status": "PASS"}]'

            Critic(session=session_spy).evaluate(
                should=[
                    {"characteristic": "first thing", "failure": "x"},
                    {"characteristic": "second thing", "failure": "y"},
                ],
                evidence_source=dummy_path, working_dir=dummy_path,
            )

            prompt = session_spy.run.call_args.kwargs["prompt"]
            assert "- first thing\n- second thing" in prompt

    class TestCallsSession:
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

    class TestParsesResponse:
        @pytest.mark.parametrize("agent_response", [
            case(
                "prose-before-json",
                'Based on my evaluation:\n\n[{"characteristic": "any", "status": "PASS"}]'
            ),
            case(
                "code-fenced-json",
                '```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n'
            ),
            case(
                "prose-before-fenced-json",
                'Based on the transcript:\n\n```json\n[{"characteristic": "any", "status": "PASS"}]\n```\n'
            ),
        ])
        def test_evaluation_should_tolerate_wrapped_json(self, dummy_path, dummy_characteristic, agent_response):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = agent_response

            Critic(session=session_stub).evaluate(
                evidence_source=dummy_path,
                working_dir=dummy_path,
                should=dummy_characteristic,
            )

    class TestPasses:
        def test_evaluation_should_not_raise_when_all_characteristics_pass(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = (
                '[{"characteristic": "first", "status": "PASS"},'
                ' {"characteristic": "second", "status": "PASS"}]'
            )

            with does_not_raise():
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "first", "failure": "should never see this"},
                        {"characteristic": "second", "failure": "neither this"},
                    ],
                )

    class TestErrors:
        def test_evaluation_should_raise_when_the_scorecard_is_empty(self, dummy_path, dummy):
            with pytest.raises(ValueError) as excinfo:
                Critic(session=dummy).evaluate(
                    should=[],
                    evidence_source=dummy_path, working_dir=dummy_path,
                )

            assert str(excinfo.value) == "scorecard must not be empty"

        def test_evaluation_should_raise_ValueError_with_cause_when_response_is_not_valid_json(self, dummy_path, dummy_characteristic):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = "not valid json."

            with pytest.raises(ValueError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=dummy_characteristic,
                )

            assert str(excinfo.value) == "response did not contain valid JSON: 'not valid json.'"
            assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)

        def test_evaluation_should_list_every_malformed_response_row(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = (
                '[{"name": "alpha", "status": "PASS"},'
                ' {"characteristic": "beta", "status": "PASS"},'
                ' {"characteristic": "gamma", "result": "FAIL"}]'
            )

            with pytest.raises(ValueError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "alpha", "failure": "x"},
                        {"characteristic": "beta", "failure": "y"},
                        {"characteristic": "gamma", "failure": "z"},
                    ],
                )

            assert str(excinfo.value) == (
                "malformed rows:\n"
                "- missing 'characteristic': {'name': 'alpha', 'status': 'PASS'}\n"
                "- missing 'status': {'characteristic': 'gamma', 'result': 'FAIL'}"
            )

        def test_evaluation_should_list_every_duplicated_characteristic(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = (
                '[{"characteristic": "alpha", "status": "PASS"},'
                ' {"characteristic": "alpha", "status": "FAIL"},'
                ' {"characteristic": "beta", "status": "PASS"},'
                ' {"characteristic": "gamma", "status": "PASS"},'
                ' {"characteristic": "gamma", "status": "FAIL"}]'
            )

            with pytest.raises(ValueError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "alpha", "failure": "x"},
                        {"characteristic": "beta", "failure": "y"},
                        {"characteristic": "gamma", "failure": "z"},
                    ],
                )

            assert str(excinfo.value) == (
                "duplicated characteristics:\n"
                "- alpha: PASS\n"
                "- alpha: FAIL\n"
                "- gamma: PASS\n"
                "- gamma: FAIL"
            )

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

        def test_evaluation_should_list_every_unexpected_characteristic(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = (
                '[{"characteristic": "expected", "status": "PASS"},'
                ' {"characteristic": "first invented", "status": "PASS"},'
                ' {"characteristic": "second invented", "status": "FAIL"}]'
            )

            with pytest.raises(ValueError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[{"characteristic": "expected", "failure": "x"}],
                )

            assert str(excinfo.value) == "unexpected characteristics: first invented, second invented"

        def test_evaluation_should_report_every_validation_problem_together(self, dummy_path):
            session_stub = MagicMock(spec=ClaudeSession)
            session_stub.run.return_value = (
                '[{"characteristic": "alpha", "status": "PASS"},'
                ' {"characteristic": "alpha", "status": "FAIL"},'
                ' {"characteristic": "invented", "status": "PASS"}]'
            )

            with pytest.raises(ValueError) as excinfo:
                Critic(session=session_stub).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "alpha", "failure": "x"},
                        {"characteristic": "missing", "failure": "y"},
                    ],
                )

            assert str(excinfo.value) == (
                "duplicated characteristics:\n"
                "- alpha: PASS\n"
                "- alpha: FAIL\n"
                "\n"
                "unaccounted characteristics: missing\n"
                "\n"
                "unexpected characteristics: invented"
            )
