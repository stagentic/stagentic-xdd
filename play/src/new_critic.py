import json


def _strip_code_fence(result):
    stripped = result.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1]
        stripped = stripped.rsplit("```", 1)[0]
    return stripped


class NewCritic:
    def __init__(self, *, session):
        self._session = session

    def evaluate(self, *, evidence, working_dir, should):
        prompt = f"{evidence}\n{working_dir}"
        result = self._session.run(prompt=prompt, working_dir=working_dir, transcript_path=working_dir / "critique.md")
        try:
            rows = json.loads(_strip_code_fence(result))
            statuses = {row["characteristic"]: row["status"] for row in rows}
        except (json.JSONDecodeError, KeyError) as err:
            raise ValueError(f"unaccounted characteristics: response was not valid JSON: {result!r}") from err
        unaccounted = [row for row in should if row["characteristic"] not in statuses]
        if unaccounted:
            names = ", ".join(row["characteristic"] for row in unaccounted)
            raise ValueError(f"unaccounted characteristics: {names}")
        failures = [row for row in should if statuses.get(row["characteristic"]) == "FAIL"]
        if failures:
            raise AssertionError(failures)
