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

    def test_from_raises_when_there_are_no_results(self):
        no_results = []
        dummy_scorecard = []

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=no_results,
                should=dummy_scorecard
            )

        assert str(excinfo.value) == "results must not be empty"

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

    @pytest.mark.parametrize("results, expected_message", [
        case(
            "all-duplicated",
            [
                {"characteristic": "alpha", "status": "PASS"},
                {"characteristic": "alpha", "status": "FAIL"},
            ],
            "duplicated characteristics:\n"
            "- alpha: PASS\n"
            "- alpha: FAIL",
        ),
        case(
            "some-duplicated",
            [
                {"characteristic": "beta", "status": "PASS"},
                {"characteristic": "alpha", "status": "PASS"},
                {"characteristic": "beta", "status": "FAIL"},
            ],
            "duplicated characteristics:\n"
            "- beta: PASS\n"
            "- beta: FAIL",
        ),
    ])
    def test_from_lists_a_duplicated_characteristic(self, results, expected_message):
        dummy_scorecard = []

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=results,
                should=dummy_scorecard
            )

        assert str(excinfo.value) == expected_message
