import json


class Critic:
    def __init__(self, *, session):
        self._session = session

    def evaluate(self, *, evidence, working_dir, should):
        characteristics = "\n".join(f"- {row['characteristic']}" for row in should)
        prompt = (
            f"Transcript: {evidence}\n"
            f"Workspace: {working_dir}\n\n"
            f"Evaluate each of the following characteristics against the transcript and workspace.\n"
            f"Respond with a JSON array where each element has 'characteristic' and 'status' (PASS or FAIL).\n\n"
            f"Characteristics:\n{characteristics}"
        )
        result = self._session.run(
            prompt=prompt,
            working_dir=working_dir,
            transcript_path=working_dir / "critique.md"
        )
        try:
            rows = json.loads(_strip_code_fence(result))
            statuses = {row["characteristic"]: row["status"] for row in rows}
        except json.JSONDecodeError as err:
            raise ValueError(f"response was not valid JSON: {result!r}") from err
        unaccounted = [row for row in should if row["characteristic"] not in statuses]
        if unaccounted:
            names = ", ".join(row["characteristic"] for row in unaccounted)
            raise ValueError(f"unaccounted characteristics: {names}")
        failures = [row for row in should if statuses.get(row["characteristic"]) == "FAIL"]
        if failures:
            lines = [f"- {row['characteristic']}: {row['failure']}" for row in failures]
            raise AssertionError("\n".join(lines))


def _strip_code_fence(result):
    stripped = result.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1]
        stripped = stripped.rsplit("```", 1)[0]
    return stripped
