from pathlib import Path

from claude_session import ClaudeSession


class Agent:
    def __init__(self, *, tasks: Path, session: ClaudeSession):
        self._tasks = tasks
        self._session = session

    def perform(self, *, task: str, working_dir: Path):
        prompt = (self._tasks / task / "TASK.md").read_text()
        self.transcript = working_dir / "transcript.md"

        self._session.run(
            prompt=prompt,
            working_dir=working_dir,
            transcript_path=self.transcript
        )
