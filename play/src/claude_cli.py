import subprocess as _subprocess_module
from collections.abc import Callable


class ClaudeCli:
    def __init__(self, subprocess: Callable = _subprocess_module.run):
        self._subprocess = subprocess

    def __call__(self, prompt):
        result = _submit_to(self._subprocess, prompt)
        if _is_not_success_exit_code(result):
            raise RuntimeError(result.stderr)
        return result.stdout


def _submit_to(subprocess, prompt):
    return subprocess(_command(prompt), capture_output=True, text=True)


def _is_not_success_exit_code(result) -> bool:
    return result.returncode != 0


def _command(prompt):
    return ["claude", "--permission-mode", "acceptEdits", "-p", prompt]
