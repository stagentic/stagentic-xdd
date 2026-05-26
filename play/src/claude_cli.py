import subprocess as _subprocess_module
from collections.abc import Callable


class ClaudeCli:
    def __init__(self, subprocess: Callable = _subprocess_module.run):
        self._subprocess = subprocess

    def __call__(self, prompt):
        result = self._subprocess(_command(prompt), capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        return result.stdout


def _command(prompt):
    return ["claude", "--permission-mode", "acceptEdits", "-p", prompt]
