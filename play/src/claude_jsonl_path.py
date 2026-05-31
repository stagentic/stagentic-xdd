from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class ClaudeJsonlPath:
    home: Path
    working_dir: Path
    session_id: str

    def __fspath__(self):
        return str(self)

    def __str__(self):
        return str(
            self.home /
            ".claude" /
            "projects" /
            _claude_encoded(self.working_dir) /
            f"{self.session_id}.jsonl"
        )


def _claude_encoded(path):
    return str(path).replace("/", "-").replace("_", "-")
