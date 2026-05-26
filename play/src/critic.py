class Critic:
    def __init__(self, claude=None):
        self._claude = claude

    def evaluate(self, *, evidence, working_dir=None, scorecard):
        if self._claude is None:
            raise ValueError("no claude implementation provided")
        prompt = f"Transcript: {evidence}\nWorkspace: {working_dir}"
        result = self._claude(prompt)
        failed_names = {
            line[len("FAIL: "):].strip()
            for line in result.splitlines()
            if line.startswith("FAIL: ")
        }
        failures = [row for row in scorecard if row["characteristic"] in failed_names]
        if failures:
            raise AssertionError(failures)
