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
                {"characteristic": "second characteristic",
                 "verify": lambda transcript: False,
                 "failure": "second failure"},
            ],
        )

    message = str(excinfo.value)
    assert "first characteristic" in message
    assert "first failure" in message
    assert "second characteristic" in message
    assert "second failure" in message
