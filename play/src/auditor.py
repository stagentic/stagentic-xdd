class Auditor:
    def evaluate(self, *, scorecard, evidence):
        row = scorecard[0]
        if not row["verify"](evidence):
            raise AssertionError(row)
