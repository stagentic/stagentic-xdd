class Critic:
    def __init__(self, claude=None):
        self._claude = claude

    def evaluate(self, *, evidence, working_dir=None, scorecard):
        _require_claude(self._claude)
        prompt = _build_prompt(evidence, working_dir)
        result = self._claude(prompt)
        failures = _failures_from(result, scorecard)
        if failures:
            raise AssertionError(failures)


def _require_claude(claude):
    if claude is None:
        raise ValueError("no claude implementation provided")


def _build_prompt(evidence, working_dir):
    return f"Transcript: {evidence}\nWorkspace: {working_dir}"


def _failures_from(result, scorecard):
    failed_names = {
        line[len("FAIL: "):].strip()
        for line in result.splitlines()
        if line.startswith("FAIL: ")
    }
    return [row for row in scorecard if row["characteristic"] in failed_names]
