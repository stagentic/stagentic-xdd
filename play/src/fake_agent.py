import subprocess


class FakeAgent:
    def __init__(self, *, tasks):
        self._tasks = tasks

    def perform(self, *, task, working_dir):
        subprocess.run(
            ["bash", str(self._tasks / f"{task}.sh")],
            cwd=working_dir,
            check=True,
        )
        self.transcript = working_dir / "transcript.md"
