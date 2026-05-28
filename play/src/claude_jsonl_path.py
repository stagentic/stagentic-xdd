from pathlib import Path


class ClaudeJsonlPath:
    def __init__(
            self, *,
            home: Path,
            working_dir: Path,
            session_id: str
    ):
        self._home = home
        self._working_dir = working_dir
        self._session_id = session_id

    def __fspath__(self):
        return str(self)

    def __str__(self):
        return str(
            self._home /
            ".claude" /
            "projects" /
            _claude_encoded(self._working_dir) /
            f"{self._session_id}.jsonl"
        )


def _claude_encoded(path):
    return str(path).replace("/", "-").replace("_", "-")
