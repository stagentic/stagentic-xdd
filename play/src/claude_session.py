import uuid
from pathlib import Path

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from transcriber import Transcriber


class ClaudeSession:
    def __init__(
            self,
            claude: ClaudeCli,
            transcriber: Transcriber,
            home: Path
    ):
        self._call_claude_with = claude
        self._transcribe_using = transcriber
        self._home = home

    def run(
            self, *,
            prompt: str,
            working_dir: Path,
            transcript_path: Path
    ):
        session_id = str(uuid.uuid4())
        result = self._call_claude_with(
            prompt=prompt,
            workspace=working_dir,
            session_id=session_id
        )
        self._transcribe_using(
            self._jsonl_path_for(session_id, working_dir),
            transcript_path
        )
        return result

    def _jsonl_path_for(
            self,
            session_id: str,
            working_dir: Path
    ) -> ClaudeJsonlPath:
        return ClaudeJsonlPath(
            home=self._home,
            working_dir=working_dir,
            session_id=session_id
        )
