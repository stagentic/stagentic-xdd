import pytest
from test_doubles.stubbed_claude_cli import StubbedClaudeCli

from critic import Critic


class TestCritic:
    def test_evaluate_raises_ValueError_when_no_claude_provided(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(ValueError):
            Critic().evaluate(
                evidence=dummy_transcript,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "my characteristic",
                     "failure": "my failure message"},
                ],
            )

    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(AssertionError) as excinfo:
            Critic(claude=StubbedClaudeCli(
                '[{"characteristic": "my characteristic", "status": "FAIL"}]'
            )).evaluate(
                evidence=dummy_transcript,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "my characteristic",
                     "failure": "my failure message"},
                ],
            )

        assert "my characteristic" in str(excinfo.value)
        assert "my failure message" in str(excinfo.value)

    def test_evaluate_returns_none_when_all_characteristics_pass(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        Critic(claude=StubbedClaudeCli(
            '[{"characteristic": "always passes", "status": "PASS"}]'
        )).evaluate(
            evidence=dummy_transcript,
            working_dir=tmp_path,
            should=[
                {"characteristic": "always passes",
                 "failure": "should never see this"},
            ],
        )

    def test_evaluate_passes_evidence_and_working_dir_to_claude(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")
        working_dir = tmp_path / "workspace"

        received = []

        def capture(prompt, **kwargs):
            received.append(prompt)
            return '[{"characteristic": "some characteristic", "status": "PASS"}]'

        Critic(claude=capture).evaluate(
            evidence=dummy_transcript,
            working_dir=working_dir,
            should=[
                {"characteristic": "some characteristic",
                 "failure": "some failure"},
            ],
        )

        assert str(dummy_transcript) in received[0]
        assert str(working_dir) in received[0]

    def test_evaluate_passes_working_dir_as_workspace_to_claude(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")
        working_dir = tmp_path / "workspace"

        received_kwargs = []

        def capture(prompt, **kwargs):
            received_kwargs.append(kwargs)
            return '[{"characteristic": "some characteristic", "status": "PASS"}]'

        Critic(claude=capture).evaluate(
            evidence=dummy_transcript,
            working_dir=working_dir,
            should=[{"characteristic": "some characteristic", "failure": "some failure"}],
        )

        assert received_kwargs[0].get("workspace") == working_dir

    def test_evaluate_handles_json_wrapped_in_markdown_code_fence(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        Critic(claude=StubbedClaudeCli(
            '```json\n[{"characteristic": "always passes", "status": "PASS"}]\n```\n'
        )).evaluate(
            evidence=dummy_transcript,
            working_dir=tmp_path,
            should=[{"characteristic": "always passes", "failure": "should never see this"}],
        )

    def test_evaluate_raises_ValueError_when_response_is_not_valid_json(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(ValueError, match="unaccounted"):
            Critic(claude=StubbedClaudeCli("I cannot access those files.")).evaluate(
                evidence=dummy_transcript,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "my characteristic", "failure": "my failure"},
                ],
            )

    def test_evaluate_passes_session_id_to_claude(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")
        received_kwargs = []

        def capture(prompt, **kwargs):
            received_kwargs.append(kwargs)
            return '[{"characteristic": "always passes", "status": "PASS"}]'

        Critic(claude=capture).evaluate(
            evidence=dummy_transcript,
            working_dir=tmp_path,
            should=[{"characteristic": "always passes", "failure": "should never see this"}],
        )

        assert "session_id" in received_kwargs[0]

    def test_failure_message_lists_every_failed_row(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(AssertionError) as excinfo:
            Critic(claude=StubbedClaudeCli(
                '[{"characteristic": "first characteristic", "status": "FAIL"},'
                ' {"characteristic": "middle characteristic", "status": "PASS"},'
                ' {"characteristic": "third characteristic", "status": "FAIL"}]'
            )).evaluate(
                evidence=dummy_transcript,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "first characteristic",
                     "failure": "first failure"},
                    {"characteristic": "middle characteristic",
                     "failure": "middle failure"},
                    {"characteristic": "third characteristic",
                     "failure": "third failure"},
                ],
            )

        message = str(excinfo.value)
        assert "first characteristic" in message
        assert "first failure" in message

        assert "middle characteristic" not in message
        assert "middle failure" not in message

        assert "third characteristic" in message
        assert "third failure" in message
