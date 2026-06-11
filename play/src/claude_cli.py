import subprocess as _subprocess_module
from collections.abc import Callable
from pathlib import Path
from subprocess import CompletedProcess


class ClaudeCli:
    def __init__(self, subprocess: Callable = _subprocess_module.run):
        self._subprocess = subprocess

    def __call__(
            self, prompt: str, *,
            workspace: Path | None = None,
            session_id: str | None = None,
    ) -> str:
        result = _submit_to(self._subprocess, prompt, workspace, session_id)
        if _is_not_successful(result):
            raise RuntimeError(result.stderr)
        return result.stdout


def _submit_to(
        subprocess: Callable, prompt: str,
        workspace: Path | None, session_id: str | None,
) -> CompletedProcess:
    return subprocess(
        _command(prompt, workspace, session_id),
        cwd=workspace,
        capture_output=True,
        text=True
    )


def _is_not_successful(result: CompletedProcess) -> bool:
    return result.returncode != 0


def _command(prompt: str, workspace: Path | None, session_id: str | None) -> list[str]:
    cmd = ["claude", "--permission-mode", "acceptEdits"]
    if session_id is not None:
        cmd += ["--session-id", session_id]
    if workspace is not None:
        cmd += ["--add-dir", str(workspace)]
    cmd += ["-p", prompt]
    return cmd
