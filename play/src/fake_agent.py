import subprocess
from pathlib import Path

from result import Success


class FakeAgent:
    def __init__(self, *, tasks_root: Path):
        self._tasks_root = tasks_root

    def perform(self, *, task: str, working_dir: Path) -> Success:
        command = str(self._tasks_root / task / "fake-task.sh")
        subprocess.run(
            ["bash", command],
            cwd=working_dir,
            check=True,
        )
        transcript_path = working_dir / "transcript.md"
        self.transcript = transcript_path
        return Success(transcript_path)
