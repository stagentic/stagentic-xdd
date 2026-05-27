import json
import uuid


class Critic:
    def __init__(self, claude=None):
        self._claude = claude

    def evaluate(self, *, evidence, working_dir=None, should):
        _require_claude(self._claude)
        prompt = _build_prompt(evidence, working_dir, should)
        sid = str(uuid.uuid4())
        result = self._claude(prompt, workspace=working_dir, session_id=sid)
        failures = _failures_from(result, should)
        if failures:
            raise AssertionError(failures)


def _require_claude(claude):
    if claude is None:
        raise ValueError("no claude implementation provided")


def _build_prompt(evidence, working_dir, should):
    characteristics = "\n".join(f"- {row['characteristic']}" for row in should)
    return (
        f"Transcript: {evidence}\n"
        f"Workspace: {working_dir}\n\n"
        f"Evaluate each of the following characteristics against the transcript and workspace.\n"
        f"Respond with a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
        f"Characteristics:\n{characteristics}"
    )


def _strip_code_fence(result):
    stripped = result.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1]
        stripped = stripped.rsplit("```", 1)[0]
    return stripped


def _failures_from(result, should):
    try:
        rows = json.loads(_strip_code_fence(result))
        statuses = {row["characteristic"]: row["status"] for row in rows}
    except (json.JSONDecodeError, KeyError):
        raise ValueError(f"unaccounted characteristics: response was not valid JSON: {result!r}")

    unaccounted = [row for row in should if row["characteristic"] not in statuses]
    if unaccounted:
        names = ", ".join(row["characteristic"] for row in unaccounted)
        raise ValueError(f"unaccounted characteristics: {names}")

    return [row for row in should if statuses.get(row["characteristic"]) == "FAIL"]
