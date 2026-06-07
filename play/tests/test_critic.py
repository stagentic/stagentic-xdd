from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest

from claude_session import ClaudeSession
from critic import Critic
from failure_message import formatted_failures_for


class TestCritic:
    @pytest.fixture
    def dummy_path(self): return Path("/dummy")

    @pytest.fixture
    def dummy_characteristic(self): return [{"characteristic": "any", "failure": "n/a"}]

    @pytest.fixture
    def session_that_passes(self):
        session = MagicMock(spec=ClaudeSession)
        session.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'
        return session

    class TestFails:
        def test_evaluation_should_call_session_and_raise_for_failed_characteristics(self, tmp_path):
            evidence_source = tmp_path / "transcript.md"
            working_dir = tmp_path / "workspace"
            session_that_fails = MagicMock(spec=ClaudeSession)
            session_that_fails.run.return_value = '[{"characteristic": "alpha", "status": "FAIL"}]'

            with pytest.raises(AssertionError) as excinfo:
                Critic(session=session_that_fails).evaluate(
                    evidence_source=evidence_source,
                    working_dir=working_dir,
                    should=[{"characteristic": "alpha", "failure": "alpha reason"}],
                )

            session_that_fails.run.assert_called_once_with(
                prompt=ANY, working_dir=ANY, transcript_path=ANY,
            )
            assert str(excinfo.value) == formatted_failures_for([
                {"characteristic": "alpha", "failure": "alpha reason"},
            ])

    class TestPasses:
        def test_evaluation_should_not_raise_when_all_characteristics_pass(self, dummy_path):
            session_that_passes = MagicMock(spec=ClaudeSession)
            session_that_passes.run.return_value = (
                '[{"characteristic": "first", "status": "PASS"},'
                ' {"characteristic": "second", "status": "PASS"}]'
            )

            with does_not_raise():
                Critic(session=session_that_passes).evaluate(
                    evidence_source=dummy_path,
                    working_dir=dummy_path,
                    should=[
                        {"characteristic": "first", "failure": "should never see this"},
                        {"characteristic": "second", "failure": "neither this"},
                    ],
                )

    class TestBuildsPrompt:
        def test_evaluation_should_include_distinct_evidence_source_in_prompt(self, dummy_path, dummy_characteristic, session_that_passes, tmp_path):
            evidence_source = tmp_path / "different_transcript.md"

            Critic(session=session_that_passes).evaluate(
                evidence_source=evidence_source,
                working_dir=dummy_path, should=dummy_characteristic,
            )

            prompt = session_that_passes.run.call_args.kwargs["prompt"]
            assert str(evidence_source) in prompt

        def test_evaluation_should_embed_working_dir_in_prompt(self, dummy_path, dummy_characteristic, session_that_passes, tmp_path):
            Critic(session=session_that_passes).evaluate(
                working_dir=tmp_path / "embedded_in_prompt",
                evidence_source=dummy_path, should=dummy_characteristic,
            )

            prompt = session_that_passes.run.call_args.kwargs["prompt"]
            assert str(tmp_path / "embedded_in_prompt") in prompt

        def test_evaluation_should_list_characteristic_names_in_prompt(self, dummy_path):
            session_that_passes = MagicMock(spec=ClaudeSession)
            session_that_passes.run.return_value = (
                '[{"characteristic": "first thing", "status": "PASS"},'
                ' {"characteristic": "second thing", "status": "PASS"}]'
            )

            Critic(session=session_that_passes).evaluate(
                should=[
                    {"characteristic": "first thing", "failure": "n/a"},
                    {"characteristic": "second thing", "failure": "n/a"},
                ],
                evidence_source=dummy_path, working_dir=dummy_path,
            )

            prompt = session_that_passes.run.call_args.kwargs["prompt"]
            assert "- first thing\n- second thing" in prompt

    class TestCallsSession:
        def test_evaluation_should_pass_working_dir_to_session(self, dummy_path, dummy_characteristic, session_that_passes, tmp_path):
            Critic(session=session_that_passes).evaluate(
                working_dir=tmp_path / "passed_to_session",
                evidence_source=dummy_path, should=dummy_characteristic,
            )

            session_that_passes.run.assert_called_once_with(
                working_dir=tmp_path / "passed_to_session",
                prompt=ANY, transcript_path=ANY,
            )

        def test_evaluation_should_derive_critique_path_from_working_dir(self, dummy_path, dummy_characteristic, session_that_passes, tmp_path):
            Critic(session=session_that_passes).evaluate(
                working_dir=tmp_path / "derives_critique_path",
                evidence_source=dummy_path, should=dummy_characteristic,
            )

            session_that_passes.run.assert_called_once_with(
                transcript_path=tmp_path / "derives_critique_path" / "critique.md",
                prompt=ANY, working_dir=ANY,
            )

    class TestErrors:
        def test_evaluation_should_raise_when_the_scorecard_is_empty(self, dummy_path, dummy):
            with pytest.raises(ValueError) as excinfo:
                Critic(session=dummy).evaluate(
                    should=[],
                    evidence_source=dummy_path, working_dir=dummy_path,
                )

            assert str(excinfo.value) == "scorecard must not be empty"
