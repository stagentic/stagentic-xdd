import subprocess


class FakeAgent:
    def __init__(self, *, tasks_root):
        self._tasks_root = tasks_root

    def perform(self, *, task, working_dir):
        command = str(self._tasks_root / task / "fake-task.sh")
        subprocess.run(
            ["bash", command],
            cwd=working_dir,
            check=True,
        )
        self.transcript = working_dir / "transcript.md"
