import pytest

from auditor import Auditor


def test_evaluate_returns_none_for_a_passing_scorecard(tmp_path):
    dummy_transcript = tmp_path / "transcript.md"
    dummy_transcript.write_text("anything")

    Auditor().evaluate(
        evidence=dummy_transcript,
        scorecard=[
            {"characteristic": "always passes",
             "verify": lambda transcript: True,
             "failure": "should never see this"},
        ],
    )


def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(tmp_path):
    dummy_transcript = tmp_path / "transcript.md"
    dummy_transcript.write_text("anything")

    with pytest.raises(AssertionError) as excinfo:
        Auditor().evaluate(
            evidence=dummy_transcript,
            scorecard=[
                {"characteristic": "my characteristic",
                 "verify": lambda transcript: False,
                 "failure": "my failure message"},
            ],
        )

    assert "my characteristic" in str(excinfo.value)
    assert "my failure message" in str(excinfo.value)


def test_failure_message_lists_every_failed_row(tmp_path):
    dummy_transcript = tmp_path / "transcript.md"
    dummy_transcript.write_text("anything")

    with pytest.raises(AssertionError) as excinfo:
        Auditor().evaluate(
            evidence=dummy_transcript,
            scorecard=[
                {"characteristic": "first characteristic",
                 "verify": lambda transcript: False,
                 "failure": "first failure"},
                {"characteristic": "middle characteristic",
                 "verify": lambda transcript: True,
                 "failure": "middle failure"},
                {"characteristic": "third characteristic",
                 "verify": lambda transcript: False,
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


def test_verify_receives_the_evidence_text(tmp_path):
    dummy_transcript = tmp_path / "transcript.md"
    dummy_transcript.write_text("hello agent")

    seen = []

    def capture(transcript):
        seen.append(transcript)
        return True

    Auditor().evaluate(
        evidence=dummy_transcript,
        scorecard=[
            {"characteristic": "captures input",
             "verify": capture,
             "failure": "n/a"},
        ],
    )

    assert seen == ["hello agent"]
