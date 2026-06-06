from pathlib import Path

from failure_message import formatted_failures_for
from raise_if import raise_if


class Auditor:
    # noinspection PyMethodMayBeStatic
    # - to preserve consistency with Critic.evaluate
    def evaluate(self, *, evidence_source: Path, working_dir: Path, should: list[dict]):
        if not should: raise ValueError("scorecard must not be empty")

        evidence_content = evidence_source.read_text()
        raise_if(
            _failures_from(evidence_content, working_dir, should),
            raising_error=AssertionError,
            with_message=_formatted_failures,
        )


def _failures_from(content: str, working_dir: Path, should: list[dict]) -> list[dict]:
    return [row for row in should if not row["verify"](content, working_dir)]


def _formatted_failures(failures: list[dict]) -> str:
    return formatted_failures_for(_entries_from(failures))


def _entries_from(failures: list[dict]) -> list[dict[str, str]]:
    return [{"characteristic": row["characteristic"], "failure": row["failure"]} for row in failures]
