import subprocess as _subprocess_module
from collections.abc import Callable


class ClaudeCli:
    def __init__(self, subprocess: Callable = _subprocess_module.run):
        self._subprocess = subprocess

    def __call__(self, prompt, *, workspace=None):
        result = _submit_to(self._subprocess, prompt, workspace)
        if _is_not_success_exit_code(result):
            raise RuntimeError(result.stderr)
        return result.stdout


def _submit_to(subprocess, prompt, workspace):
    return subprocess(_command(prompt, workspace), capture_output=True, text=True)


def _is_not_success_exit_code(result) -> bool:
    return result.returncode != 0


def _command(prompt, workspace=None):
    cmd = ["claude", "--permission-mode", "acceptEdits"]
    if workspace is not None:
        cmd += ["--add-dir", str(workspace)]
    cmd += ["-p", prompt]
    return cmd
