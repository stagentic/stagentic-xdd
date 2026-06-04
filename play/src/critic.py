import json
from collections import Counter
from collections.abc import Callable
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

        rows = _rows_unless(
            result,
            has_problem=_malformed,
            raising_error=ValueError,
            with_message=_formatted_malformed,
        )

        statuses = _statuses_from(rows)
        _raise_if(
            _problems_in([
                _duplicates_problem(rows),
                _unaccounted_problem(should, statuses),
                _unexpected_problem(should, statuses),
            ]),
            raising_error=ValueError,
            with_message=_problems_message,
        )

        _raise_if(
            _failures_in(should, statuses),
            raising_error=AssertionError,
            with_message=_failure_message,
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


def _rows_unless(
        result: str, *,
        has_problem: Callable[[list[dict]], list],
        raising_error: type[Exception],
        with_message: Callable[[list], str],
) -> list[dict]:
    rows = _rows_from(result)
    _raise_if(has_problem(rows), raising_error=raising_error, with_message=with_message)
    return rows


def _rows_from(result: str) -> list[dict]:
    try:
        return json.loads(
            _unwrap_json_response(result)
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"response did not contain valid JSON: {result!r}") from err


def _unwrap_json_response(result: str) -> str:
    text = result.strip()
    stages = (
        _remove_content_before_json,
        _remove_content_after_json,
    )
    for chisel in stages:
        text = chisel(text)
    return text


def _remove_content_before_json(text: str) -> str:
    start = _start_of_json(text)
    return text if start is None else text[start:]


def _start_of_json(text: str) -> int | None:
    decoder = json.JSONDecoder()
    end = len(text)
    while (start := text.rfind("[", 0, end)) != -1:
        try:
            content, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            end = start
            continue
        if _is_scorecard(content): return start
        end = start
    return None


def _is_scorecard(content) -> bool:
    return isinstance(content, list) and all(
        isinstance(row, dict) and "characteristic" in row and "status" in row
        for row in content
    )


def _remove_content_after_json(text: str) -> str:
    try:
        _, end = json.JSONDecoder().raw_decode(text)
    except json.JSONDecodeError:
        return text
    return text[:end]


_REQUIRED_KEYS = ("characteristic", "status")


def _malformed(rows: list[dict]) -> list[dict]:
    return [row for row in rows if not all(k in row for k in _REQUIRED_KEYS)]


def _raise_if(
        items: list, *,
        raising_error: type[Exception],
        with_message: Callable[[list], str],
) -> None:
    if items: raise raising_error(with_message(items))


def _formatted_malformed(malformed: list[dict]) -> str:
    return "malformed rows:\n" + "\n".join(
        _formatted_malformed_row(row) for row in malformed
    )


def _formatted_malformed_row(row: dict) -> str:
    missing = ", ".join(repr(k) for k in _REQUIRED_KEYS if k not in row)
    return f"- missing {missing}: {row}"


def _statuses_from(rows: list[dict]) -> dict[str, str]:
    return {row["characteristic"]: row["status"] for row in rows}


def _duplicates_problem(rows: list[dict]) -> str | None:
    duplicated = _duplicated_in(rows)
    return _formatted_duplicates(rows, duplicated) if duplicated else None


def _duplicated_in(rows: list[dict]) -> set[str]:
    counts = Counter(row["characteristic"] for row in rows)
    return {name for name, count in counts.items() if count > 1}


def _formatted_duplicates(rows: list[dict], duplicated: set[str]) -> str:
    return "duplicated characteristics:\n" + "\n".join(
        f"- {row['characteristic']}: {row['status']}"
        for row in rows if row['characteristic'] in duplicated
    )


def _unaccounted_problem(should: list[dict], statuses: dict[str, str]) -> str | None:
    unaccounted = _unaccounted_for(should, statuses)
    return _formatted_unaccounted(unaccounted) if unaccounted else None


def _unaccounted_for(should: list[dict], statuses: dict[str, str]) -> list[str]:
    return [row["characteristic"] for row in should if row["characteristic"] not in statuses]


def _formatted_unaccounted(unaccounted: list[str]) -> str:
    return f"unaccounted characteristics: {', '.join(unaccounted)}"


def _unexpected_problem(should: list[dict], statuses: dict[str, str]) -> str | None:
    unexpected = _unexpected_in(statuses, should)
    return _formatted_unexpected(unexpected) if unexpected else None


def _unexpected_in(statuses: dict[str, str], should: list[dict]) -> list[str]:
    expected_names = {row["characteristic"] for row in should}
    return [name for name in statuses if name not in expected_names]


def _formatted_unexpected(unexpected: list[str]) -> str:
    return f"unexpected characteristics: {', '.join(unexpected)}"


def _problems_in(possible_problems: list[str | None]) -> list[str]:
    return [p for p in possible_problems if p is not None]


def _problems_message(problems: list[str]) -> str:
    return "\n\n".join(problems)


def _failures_in(should: list[dict], statuses: dict[str, str]) -> list[dict]:
    return [row for row in should if statuses.get(row["characteristic"]) == "FAIL"]


def _failure_message(failures: list[dict]) -> str:
    return "\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures)
