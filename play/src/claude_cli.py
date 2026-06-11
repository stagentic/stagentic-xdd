import subprocess
from collections.abc import Callable
from pathlib import Path


class ClaudeCli:
    def __init__(self, runner: Callable = subprocess.run):
        self._runner = runner

    def __call__(
            self, prompt: str, *,
            workspace: Path,
            session_id: str,
    ) -> str:
        result = _submit_to(
            self._runner,
            prompt,
            workspace,
            session_id
        )
        if _is_not_successful(result):
            raise RuntimeError(result.stderr)
        return result.stdout


def _submit_to(
        runner: Callable,
        prompt: str,
        workspace: Path,
        session_id: str,
) -> subprocess.CompletedProcess:
    return runner(
        _command(
            prompt,
            workspace,
            session_id
        ),
        cwd=workspace,
        capture_output=True,
        text=True
    )


def _command(
        prompt: str,
        workspace: Path,
        session_id: str
) -> list[str]:
    cmd = ["claude", "-p", prompt]
    cmd += ["--permission-mode", "acceptEdits"]
    cmd += ["--session-id", session_id]
    cmd += ["--add-dir", str(workspace)]
    return cmd


def _is_not_successful(result: subprocess.CompletedProcess) -> bool:
    return result.returncode != 0
