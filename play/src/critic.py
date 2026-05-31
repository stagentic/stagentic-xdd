import json
from pathlib import Path

from claude_session import ClaudeSession


class Critic:
    def __init__(self, *, session: ClaudeSession):
        self._session = session

    def evaluate(self, *, evidence_source: Path, working_dir: Path, should: list[dict]):
        result = self._session.run(
            prompt=_prompt_for(evidence_source, working_dir, should),
            working_dir=working_dir,
            transcript_path=working_dir / "critique.md",
        )
        statuses = _statuses_from(result)

        unaccounted = _unaccounted_for(should, statuses)
        if unaccounted: raise ValueError(
            f"unaccounted characteristics: {_names_of(unaccounted)}"
        )

        failures = _all_failures(should, statuses)
        if failures: raise AssertionError(
            _formatted(failures)
        )


def _prompt_for(evidence_source: Path, working_dir: Path, should: list[dict]) -> str:
    characteristics = "\n".join(f"- {row['characteristic']}" for row in should)
    return (
        f"Transcript: {evidence_source}\n"
        f"Workspace: {working_dir}\n\n"
        f"Evaluate each of the following characteristics against the transcript and workspace.\n"
        f"Respond with only a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
        f"Characteristics:\n{characteristics}"
    )


def _statuses_from(result):
    try:
        rows = json.loads(_strip_code_fence(result))
        return {row["characteristic"]: row["status"] for row in rows}
    except json.JSONDecodeError as err:
        raise ValueError(f"response was not valid JSON: {result!r}") from err


def _strip_code_fence(result):
    stripped = result.strip()
    fence_start = stripped.find("```")
    if fence_start != -1:
        stripped = stripped[fence_start:]
        stripped = stripped.split("\n", 1)[1]
        stripped = stripped.rsplit("```", 1)[0]
        return stripped.strip()
    array_start = stripped.find("[")
    if array_start > 0:
        stripped = stripped[array_start:]
    return stripped


def _unaccounted_for(should, statuses: dict[str, str]) -> list[dict]:
    return [row for row in should if row["characteristic"] not in statuses]


def _names_of(unaccounted: list[dict]) -> str:
    return ", ".join(row["characteristic"] for row in unaccounted)


def _all_failures(should, statuses):
    return [row for row in should if statuses.get(row["characteristic"]) == "FAIL"]


def _formatted(failures):
    return "\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures)
