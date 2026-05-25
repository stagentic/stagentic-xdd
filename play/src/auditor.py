class Auditor:
    def evaluate(self, *, evidence, scorecard):
        content = evidence.read_text()
        failures = [row for row in scorecard if not row["verify"](content)]
        if failures:
            raise AssertionError(failures)
