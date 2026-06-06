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
        should = characteristics_for_all(maybe_results)

        scorecard = ScorecardResults.from_(
            maybe_results=maybe_results,
            should=should,
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
            "missing-characteristic",
            [{"status": "PASS"}],
            "invalid rows:\n"
            "- missing 'characteristic': {'status': 'PASS'}",
        ),
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
            "missing-either-across-rows",
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
        should = characteristics_for_all(results)

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=results,
                should=should,
            )

        assert str(excinfo.value) == expected_message

    @pytest.mark.parametrize("should, expected_message", [
        case(
            "one-unaccounted",
            [
                {"characteristic": "first"},
                {"characteristic": "second"},
            ],
            "unaccounted characteristics: second",
        ),
        case(
            "two-unaccounted",
            [
                {"characteristic": "first"},
                {"characteristic": "second"},
                {"characteristic": "third"},
            ],
            "unaccounted characteristics: second, third",
        ),
    ])
    def test_from_lists_unaccounted_for_characteristics(self, should, expected_message):
        results = [{"characteristic": "first", "status": "PASS"}]

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=results,
                should=should,
            )

        assert str(excinfo.value) == expected_message

    @pytest.mark.parametrize("results, expected_message", [
        case(
            "one-unexpected",
            [
                {"characteristic": "first", "status": "PASS"},
                {"characteristic": "extra", "status": "PASS"},
            ],
            "unexpected characteristics: extra",
        ),
        case(
            "two-unexpected",
            [
                {"characteristic": "first", "status": "PASS"},
                {"characteristic": "extra", "status": "PASS"},
                {"characteristic": "other", "status": "PASS"},
            ],
            "unexpected characteristics: extra, other",
        ),
    ])
    def test_from_lists_unexpected_characteristics(self, results, expected_message):
        should = [{"characteristic": "first"}]

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=results,
                should=should,
            )

        assert str(excinfo.value) == expected_message

    def test_failures_lists_a_characteristic_that_did_not_pass(self):
        scorecard = ScorecardResults.from_(
            maybe_results=[{"characteristic": "alpha", "status": "FAIL"}],
            should=[{"characteristic": "alpha", "failure": "alpha reason"}],
        )

        assert scorecard.failures() == [{"characteristic": "alpha", "failure": "alpha reason"}]

    def test_from_reports_every_coherence_problem_together(self):
        results = [
            {"characteristic": "alpha", "status": "PASS"},
            {"characteristic": "alpha", "status": "FAIL"},
            {"characteristic": "invented", "status": "PASS"},
        ]
        should = [
            {"characteristic": "alpha"},
            {"characteristic": "missing"},
        ]

        with pytest.raises(ValueError) as excinfo:
            ScorecardResults.from_(
                maybe_results=results,
                should=should,
            )

        assert str(excinfo.value) == (
            "duplicated characteristics:\n"
            "- alpha: PASS\n"
            "- alpha: FAIL\n"
            "\n"
            "unaccounted characteristics: missing\n"
            "\n"
            "unexpected characteristics: invented"
        )


def characteristics_for_all(results):
    return [
        {"characteristic": name}
        for name in dict.fromkeys(
            result["characteristic"] for result in results
        )
    ]
