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
                scorecard=[
                    {"characteristic": "my characteristic",
                     "failure": "my failure message"},
                ],
            )

    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(AssertionError) as excinfo:
            Critic(claude=StubbedClaudeCli("FAIL: my characteristic\n")).evaluate(
                evidence=dummy_transcript,
                working_dir=tmp_path,
                scorecard=[
                    {"characteristic": "my characteristic",
                     "failure": "my failure message"},
                ],
            )

        assert "my characteristic" in str(excinfo.value)
        assert "my failure message" in str(excinfo.value)

    def test_evaluate_returns_none_for_a_passing_scorecard(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        Critic(claude=StubbedClaudeCli("PASS")).evaluate(
            evidence=dummy_transcript,
            working_dir=tmp_path,
            scorecard=[
                {"characteristic": "always passes",
                 "failure": "should never see this"},
            ],
        )

    def test_evaluate_passes_evidence_and_working_dir_to_claude(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")
        working_dir = tmp_path / "workspace"

        received = []

        def capture(prompt):
            received.append(prompt)
            return "PASS"

        Critic(claude=capture).evaluate(
            evidence=dummy_transcript,
            working_dir=working_dir,
            scorecard=[
                {"characteristic": "some characteristic",
                 "failure": "some failure"},
            ],
        )

        assert str(dummy_transcript) in received[0]
        assert str(working_dir) in received[0]

    def test_failure_message_lists_every_failed_row(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(AssertionError) as excinfo:
            Critic(claude=StubbedClaudeCli(
                "FAIL: first characteristic\n"
                "PASS: middle characteristic\n"
                "FAIL: third characteristic\n"
            )).evaluate(
                evidence=dummy_transcript,
                working_dir=tmp_path,
                scorecard=[
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
