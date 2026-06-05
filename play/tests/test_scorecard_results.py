import pytest

from scorecard_results import ScorecardResults


def case(id, *values):
    return pytest.param(*values, id=id)


class TestScorecardResults:
    @pytest.mark.parametrize("maybe_results", [
        case(
            "single-result",
            [{"characteristic": "captures input", "status": "PASS"}]
        ),
        case(
            "multiple-results",
            [
                {"characteristic": "captures input", "status": "PASS"},
                {"characteristic": "reports outcome", "status": "FAIL"},
            ]
        ),
    ])
    def test_from_exposes_the_results(self, maybe_results):
        dummy_scorecard = []

        scorecard = ScorecardResults.from_(
            maybe_results=maybe_results,
            should=dummy_scorecard
        )

        assert scorecard.results == maybe_results

    @pytest.mark.parametrize("missing_status", [
        case(
            "one-row",
            [{"characteristic": "runs the test"}]
        ),
        case(
            "one-row-in-rows",
            [
                {"characteristic": "captures input", "status": "PASS"},
                {"characteristic": "runs the test"},
            ]
        ),
    ])
    def test_from_raises_when_a_result_is_missing_status(self, missing_status):
        dummy_scorecard = []

        with pytest.raises(ValueError):
            ScorecardResults.from_(
                maybe_results=missing_status,
                should=dummy_scorecard
            )

    def test_from_raises_when_a_result_is_missing_characteristic(self):
        missing_characteristic = [{"status": "PASS"}]
        dummy_scorecard = []

        with pytest.raises(ValueError):
            ScorecardResults.from_(
                maybe_results=missing_characteristic,
                should=dummy_scorecard
            )

    @pytest.mark.parametrize("maybe_results, expected_message", [
        case(
            "missing-status",
            [{"characteristic": "runs the test"}],
            "invalid rows:\n"
            "- missing 'status': {'characteristic': 'runs the test'}",
        ),
        case(
            "missing-both",
            [{"name": "delta", "result": "FAIL"}],
            "invalid rows:\n"
            "- missing 'characteristic', 'status': {'name': 'delta', 'result': 'FAIL'}",
        ),
        case(
            "two-invalid-rows",
            [
                {"name": "alpha", "status": "PASS"},
                {"characteristic": "beta", "status": "PASS"},
                {"characteristic": "gamma", "result": "FAIL"},
            ],
            "invalid rows:\n"
            "- missing 'characteristic': {'name': 'alpha', 'status': 'PASS'}\n"
            "- missing 'status': {'characteristic': 'gamma', 'result': 'FAIL'}",
        ),
    ])
    def test_from_names_the_invalid_result_and_the_key_it_lacks(self, maybe_results, expected_message):
        dummy_scorecard = []

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=maybe_results,
                should=dummy_scorecard
            )

        assert str(excinfo.value) == expected_message

    def test_from_raises_when_there_are_no_results(self):
        no_results = []
        dummy_scorecard = []

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=no_results,
                should=dummy_scorecard
            )

        assert str(excinfo.value) == "results must not be empty"
