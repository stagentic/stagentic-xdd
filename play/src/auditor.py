class Auditor:
    def evaluate(self, *, evidence, working_dir=None, should):
        content = evidence.read_text()
        failures = [row for row in should if not row["verify"](content, working_dir)]
        if failures:
            raise AssertionError("\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures))
