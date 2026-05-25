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
