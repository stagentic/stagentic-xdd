class ClaudeCli:
    def __init__(self, subprocess=None):
        self._subprocess = subprocess

    def __call__(self, prompt):
        result = self._subprocess(["claude", "--permission-mode", "acceptEdits"],
                                  capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        return result.stdout
