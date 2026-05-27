from typing import Any


class Auditor:
    def evaluate(self, *, evidence, working_dir=None, should):
        evidence_content = evidence.read_text()
        failures = _failures_from(evidence_content, should, working_dir)
        if failures:
            raise AssertionError(_formatted(failures))


def _failures_from(content, should, working_dir) -> list[Any]:
    return [row for row in should if not row["verify"](content, working_dir)]


def _formatted(failures: list[Any]) -> str:
    return "\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures)
