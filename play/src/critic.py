import json
from collections import Counter
from pathlib import Path

from claude_session import ClaudeSession


class Critic:
    def __init__(self, *, session: ClaudeSession):
        self._session = session

    def evaluate(
            self, *,
            evidence_source: Path,
            working_dir: Path,
            should: list[dict]
    ):
        if not should: raise ValueError("scorecard must not be empty")

        result = self._session.run(
            prompt=_prompt_for(evidence_source, working_dir, should),
            working_dir=working_dir,
            transcript_path=working_dir / "critique.md",
        )

        rows = _rows_from(result)
        duplicated = _duplicated_in(rows)
        if duplicated: raise ValueError(
            _formatted_duplicates(rows, duplicated)
        )

        statuses = _statuses_from(rows)
        any_unaccounted_for = _unaccounted_for(should, statuses)
        if any_unaccounted_for: raise ValueError(
            f"unaccounted characteristics: {_names_of(any_unaccounted_for)}"
        )

        expected_names = {row["characteristic"] for row in should}
        unexpected = [name for name in statuses if name not in expected_names]
        if unexpected: raise ValueError(
            f"unexpected characteristics: {', '.join(unexpected)}"
        )

        any_failures = _all_failures(should, statuses)
        if any_failures: raise AssertionError(
            _formatted(any_failures)
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


def _rows_from(result: str) -> list[dict]:
    try:
        return json.loads(_strip_code_fence(result))
    except json.JSONDecodeError as err:
        raise ValueError(f"response did not contain valid JSON: {result!r}") from err


def _statuses_from(rows: list[dict]) -> dict[str, str]:
    return {row["characteristic"]: row["status"] for row in rows}


def _duplicated_in(rows: list[dict]) -> set[str]:
    counts = Counter(row["characteristic"] for row in rows)
    return {name for name, count in counts.items() if count > 1}


def _formatted_duplicates(rows: list[dict], duplicated: set[str]) -> str:
    return "duplicated characteristics:\n" + "\n".join(
        f"- {row['characteristic']}: {row['status']}"
        for row in rows if row['characteristic'] in duplicated
    )


def _strip_code_fence(result: str) -> str:
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


def _unaccounted_for(should: list[dict], statuses: dict[str, str]) -> list[dict]:
    return [row for row in should if row["characteristic"] not in statuses]


def _names_of(unaccounted: list[dict]) -> str:
    return ", ".join(row["characteristic"] for row in unaccounted)


def _all_failures(should: list[dict], statuses: dict[str, str]) -> list[dict]:
    return [row for row in should if statuses.get(row["characteristic"]) == "FAIL"]


def _formatted(failures: list[dict]) -> str:
    return "\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures)
