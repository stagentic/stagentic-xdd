class Auditor:
    def evaluate(self, *, evidence, working_dir=None, scorecard):
        content = evidence.read_text()
        failures = [row for row in scorecard if not row["verify"](content, working_dir)]
        if failures:
            raise AssertionError(failures)
