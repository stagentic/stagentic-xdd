from contextlib import nullcontext as does_not_raise
from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest

from claude_session import ClaudeSession
from critic import Critic
from failure_message import formatted_failures_for


class TestCritic:
    @pytest.fixture
    def working_dir(self): return Path("/workspace/coding_exercise")

    @pytest.fixture
    def evidence_source(self, working_dir): return working_dir / "transcript.md"

    @pytest.fixture
    def one_characteristic_scorecard(self): return [{"characteristic": "any", "failure": "n/a"}]

    @pytest.fixture
    def session_that_passes(self):
        session = MagicMock(spec=ClaudeSession)
        session.run.return_value = '[{"characteristic": "any", "status": "PASS"}]'
        return session

    class TestFails:
        def test_evaluation_should_call_session_and_raise_for_failed_characteristics(self, evidence_source, working_dir):
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
            prompt = session_that_fails.run.call_args.kwargs["prompt"]
            assert f"Transcript: {evidence_source}\n" in prompt
            assert f"Workspace: {working_dir}\n" in prompt
            assert "- alpha" in prompt
            assert str(excinfo.value) == formatted_failures_for([
                {"characteristic": "alpha", "failure": "alpha reason"},
            ])

    class TestPasses:
        def test_evaluation_should_not_raise_when_all_characteristics_pass(self, evidence_source, working_dir):
            session_that_passes = MagicMock(spec=ClaudeSession)
            session_that_passes.run.return_value = (
                '[{"characteristic": "first", "status": "PASS"},'
                ' {"characteristic": "second", "status": "PASS"}]'
            )

            with does_not_raise():
                Critic(session=session_that_passes).evaluate(
                    evidence_source=evidence_source,
                    working_dir=working_dir,
                    should=[
                        {"characteristic": "first", "failure": "should never see this"},
                        {"characteristic": "second", "failure": "neither this"},
                    ],
                )

    class TestBuildsPrompt:
        def test_evaluation_should_include_distinct_evidence_source_in_prompt(self, working_dir, one_characteristic_scorecard, session_that_passes):
            evidence_source = Path("/workspace/other-run/transcript.md")

            Critic(session=session_that_passes).evaluate(
                evidence_source=evidence_source,
                working_dir=working_dir, should=one_characteristic_scorecard,
            )

            prompt = session_that_passes.run.call_args.kwargs["prompt"]
            assert f"Transcript: {evidence_source}\n" in prompt

        def test_evaluation_should_embed_working_dir_in_prompt(self, evidence_source, one_characteristic_scorecard, session_that_passes):
            working_dir = Path("/workspace/embedded-in-prompt")

            Critic(session=session_that_passes).evaluate(
                working_dir=working_dir,
                evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            prompt = session_that_passes.run.call_args.kwargs["prompt"]
            assert f"Workspace: {working_dir}\n" in prompt

        def test_evaluation_should_list_characteristic_names_in_prompt(self, evidence_source, working_dir):
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
                evidence_source=evidence_source, working_dir=working_dir,
            )

            prompt = session_that_passes.run.call_args.kwargs["prompt"]
            assert "- first thing\n- second thing" in prompt

    class TestCallsSession:
        def test_evaluation_should_pass_working_dir_to_session(self, evidence_source, one_characteristic_scorecard, session_that_passes):
            working_dir = Path("/workspace/passed-to-session")

            Critic(session=session_that_passes).evaluate(
                working_dir=working_dir,
                evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                working_dir=working_dir,
                prompt=ANY, transcript_path=ANY,
            )

        def test_evaluation_should_derive_critique_path_from_working_dir(self, evidence_source, one_characteristic_scorecard, session_that_passes):
            working_dir = Path("/workspace/derives-critique-path")

            Critic(session=session_that_passes).evaluate(
                working_dir=working_dir,
                evidence_source=evidence_source, should=one_characteristic_scorecard,
            )

            session_that_passes.run.assert_called_once_with(
                transcript_path=working_dir / "critique.md",
                prompt=ANY, working_dir=ANY,
            )

    class TestErrors:
        def test_evaluation_should_raise_when_the_scorecard_is_empty(self, evidence_source, working_dir, dummy):
            with pytest.raises(ValueError) as excinfo:
                Critic(session=dummy).evaluate(
                    should=[],
                    evidence_source=evidence_source, working_dir=working_dir,
                )

            assert str(excinfo.value) == "scorecard must not be empty"
