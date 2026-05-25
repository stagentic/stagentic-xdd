class Auditor:
    def evaluate(self, *, evidence, scorecard):
        failures = [row for row in scorecard if not row["verify"](evidence)]
        if failures:
            raise AssertionError(failures)
