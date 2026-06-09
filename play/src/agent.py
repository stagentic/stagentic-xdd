from pathlib import Path

from claude_session import ClaudeSession
from result import Success


class Agent:
    def __init__(
            self, *,
            tasks_root: Path,
            session: ClaudeSession
    ):
        self._tasks_root = tasks_root
        self._session = session

    def perform(self, *, task: str, working_dir: Path) -> Success:
        transcript_path = working_dir / "transcript.md"
        self.transcript = transcript_path

        self._session.run(
            prompt=_prompt_for(
                self._tasks_root,
                task
            ),
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

        return Success(transcript_path)


def _prompt_for(tasks_root: Path, task: str) -> str:
    return (tasks_root / task / "TASK.md").read_text()
