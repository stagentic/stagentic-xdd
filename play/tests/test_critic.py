import pytest

from critic import Critic


class TestCritic:
    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, tmp_path):
        dummy_transcript = tmp_path / "transcript.md"
        dummy_transcript.write_text("anything")

        with pytest.raises(AssertionError) as excinfo:
            Critic().evaluate(
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

        always_passes = lambda prompt: "PASS"

        Critic(claude=always_passes).evaluate(
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
