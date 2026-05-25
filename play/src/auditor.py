class Auditor:
    def evaluate(self, *, scorecard, evidence):
        failures = [row for row in scorecard if not row["verify"](evidence)]
        if failures:
            raise AssertionError(failures)
