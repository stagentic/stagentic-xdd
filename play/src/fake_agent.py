import subprocess
from pathlib import Path

from result import Success


class FakeAgent:
    def __init__(self, *, tasks_root: Path):
        self._tasks_root = tasks_root

    def perform(self, *, task: str, working_dir: Path) -> Success:
        subprocess.run(
            _command_for(
                self._tasks_root, task
            ),
            cwd=working_dir,
            check=True,
        )
        transcript_path = working_dir / "transcript.md"
        self.transcript = transcript_path
        return Success(transcript_path)


def _command_for(tasks_root: Path, task: str) -> list[str]:
    return ["bash", str(tasks_root / task / "fake-task.sh")]
