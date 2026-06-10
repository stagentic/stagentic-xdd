from pathlib import Path

from failure_message import formatted_failures_for
from raise_if import raise_if
from result import Failure, Success
from scorecard_results import ScorecardResults


class Auditor:
    # noinspection PyMethodMayBeStatic
    # - to preserve consistency with Critic.evaluate
    def evaluate(self, *, evidence_source: Path, working_dir: Path, should: list[dict]):
        if not should: raise ValueError("scorecard must not be empty")

        result = self.evaluate2(
            evidence_source=evidence_source,
            working_dir=working_dir,
            should=should,
        )
        if isinstance(result, Failure):
            raise_if(
                result.value,
                raising_error=AssertionError,
                with_message=formatted_failures_for,
            )

    def evaluate2(self, *, evidence_source, working_dir, should):
        evidence_content = evidence_source.read_text()
        match _entries_from(_failures_from(evidence_content, working_dir, should)):
            case []:
                return Success(ScorecardResults(
                    should=_entries_from(should),
                    results=[{"characteristic": row["characteristic"], "status": "PASS"}
                             for row in should],
                ))
            case failures:
                return Failure(failures)


def _failures_from(content: str, working_dir: Path, should: list[dict]) -> list[dict]:
    return [row for row in should if not row["verify"](content, working_dir)]


def _entries_from(failures: list[dict]) -> list[dict[str, str]]:
    return [{"characteristic": row["characteristic"], "failure": row["failure"]} for row in failures]
