import pytest

from auditor import Auditor


def test_evaluate_returns_none_for_a_passing_scorecard(tmp_path):
    evidence = tmp_path / "transcript.md"
    evidence.write_text("anything")

    Auditor().evaluate(
        scorecard=[
            {"characteristic": "always passes",
             "verify": lambda transcript: True,
             "failure": "should never see this"},
        ],
        evidence=evidence,
    )


def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(tmp_path):
    evidence = tmp_path / "transcript.md"
    evidence.write_text("anything")

    with pytest.raises(AssertionError) as excinfo:
        Auditor().evaluate(
            scorecard=[
                {"characteristic": "my characteristic",
                 "verify": lambda transcript: False,
                 "failure": "my failure message"},
            ],
            evidence=evidence,
        )

    assert "my characteristic" in str(excinfo.value)
    assert "my failure message" in str(excinfo.value)


def test_failure_message_lists_every_failed_row(tmp_path):
    evidence = tmp_path / "transcript.md"
    evidence.write_text("anything")

    with pytest.raises(AssertionError) as excinfo:
        Auditor().evaluate(
            scorecard=[
                {"characteristic": "first characteristic",
                 "verify": lambda transcript: False,
                 "failure": "first failure"},
                {"characteristic": "second characteristic",
                 "verify": lambda transcript: False,
                 "failure": "second failure"},
            ],
            evidence=evidence,
        )

    message = str(excinfo.value)
    assert "first characteristic" in message
    assert "first failure" in message
    assert "second characteristic" in message
    assert "second failure" in message
