from pathlib import Path

from claude_session import ClaudeSession


class Agent:
    def __init__(
            self, *,
            tasks_root: Path,
            session: ClaudeSession
    ):
        self._tasks_root = tasks_root
        self._session = session

    def perform(self, *, task: str, working_dir: Path):
        self.transcript = working_dir / "transcript.md"

        self._session.run(
            prompt=_prompt_for(
                self._tasks_root,
                task
            ),
            working_dir=working_dir,
            transcript_path=self.transcript,
        )


def _prompt_for(tasks_root: Path, task: str) -> str:
    return (tasks_root / task / "TASK.md").read_text()
