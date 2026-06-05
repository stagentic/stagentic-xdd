from scorecard_results import ScorecardResults


class TestScorecardResults:
    def test_from_exposes_the_results(self):
        maybe_results = [{"characteristic": "captures input", "status": "PASS"}]
        dummy_scorecard = []

        scorecard = ScorecardResults.from_(
            maybe_results=maybe_results,
            should=dummy_scorecard
        )

        assert scorecard.results == maybe_results
