import json


class Critic:
    def __init__(self, claude=None):
        self._claude = claude

    def evaluate(self, *, evidence, working_dir=None, scorecard):
        _require_claude(self._claude)
        prompt = _build_prompt(evidence, working_dir, scorecard)
        result = self._claude(prompt, workspace=working_dir)
        failures = _failures_from(result, scorecard)
        if failures:
            raise AssertionError(failures)


def _require_claude(claude):
    if claude is None:
        raise ValueError("no claude implementation provided")


def _build_prompt(evidence, working_dir, scorecard):
    characteristics = "\n".join(f"- {row['characteristic']}" for row in scorecard)
    return (
        f"Transcript: {evidence}\n"
        f"Workspace: {working_dir}\n\n"
        f"Evaluate each of the following characteristics against the transcript and workspace.\n"
        f"Respond with a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
        f"Characteristics:\n{characteristics}"
    )


def _failures_from(result, scorecard):
    try:
        rows = json.loads(result)
        statuses = {row["characteristic"]: row["status"] for row in rows}
    except (json.JSONDecodeError, KeyError):
        raise ValueError(f"unaccounted characteristics: response was not valid JSON: {result!r}")

    unaccounted = [row for row in scorecard if row["characteristic"] not in statuses]
    if unaccounted:
        names = ", ".join(row["characteristic"] for row in unaccounted)
        raise ValueError(f"unaccounted characteristics: {names}")

    return [row for row in scorecard if statuses.get(row["characteristic"]) == "FAIL"]
