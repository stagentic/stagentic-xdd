class Critic:
    def __init__(self, claude=None):
        self._claude = claude

    def evaluate(self, *, evidence, working_dir=None, scorecard):
        prompt = f"Transcript: {evidence}\nWorkspace: {working_dir}"
        result = self._claude(prompt) if self._claude else ""
        if "PASS" not in result:
            raise AssertionError(scorecard)
