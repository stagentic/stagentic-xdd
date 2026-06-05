import json
from pathlib import Path

from claude_session import ClaudeSession
from raise_if import raise_if
from scorecard import formatted_failures_for
from scorecard_results import ScorecardResults


class Critic:
    def __init__(self, *, session: ClaudeSession):
        self._session = session

    def evaluate(
            self, *,
            evidence_source: Path,
            working_dir: Path,
            should: list[dict[str, str]]
    ):
        if not should: raise ValueError("scorecard must not be empty")

        agent_response = self._session.run(
            prompt=_prompt_for(evidence_source, working_dir, should),
            working_dir=working_dir,
            transcript_path=working_dir / "critique.md",
        )
        maybe_results = _decoded_from(
            _json_text_in(agent_response)
        )

        scorecard = ScorecardResults.from_(
            maybe_results=maybe_results,
            should=should,
        )

        raise_if(
            _failures_in(should, scorecard.results),
            raising_error=AssertionError,
            with_message=formatted_failures_for,
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


def _decoded_from(json_text: str) -> list[dict]:
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as err:
        raise ValueError(f"response did not contain valid JSON: {json_text!r}") from err


def _json_text_in(result: str) -> str:
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


def _failures_in(should: list[dict[str, str]], rows: list[dict]) -> list[dict[str, str]]:
    statuses = {row["characteristic"]: row["status"] for row in rows}
    return [row for row in should if statuses.get(row["characteristic"]) != "PASS"]
