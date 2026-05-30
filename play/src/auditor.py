from pathlib import Path


class Auditor:
    # noinspection PyMethodMayBeStatic
    # - to preserve consistency with Critic.evaluate
    def evaluate(self, *, evidence: Path, working_dir: Path | None = None, should: list[dict]):
        if not should: raise ValueError("scorecard must not be empty")

        evidence_content = evidence.read_text()
        failures = _failures_from(evidence_content, should, working_dir)

        if failures: raise AssertionError(_formatted(failures))


def _failures_from(content: str, should: list[dict], working_dir: Path | None) -> list[dict]:
    return [row for row in should if not row["verify"](content, working_dir)]


def _formatted(failures: list[dict]) -> str:
    return "\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures)
