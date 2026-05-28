import uuid


class ClaudeJsonlPath:
    def __init__(self, *, home, working_dir, session_id):
        self._home = home
        self._working_dir = working_dir
        self._session_id = session_id

    def __fspath__(self):
        return str(self)

    def __str__(self):
        return str(self._home / ".claude" / "projects" / _claude_encoded(self._working_dir) / f"{self._session_id}.jsonl")


def _claude_encoded(path):
    return str(path).replace("/", "-").replace("_", "-")


class ClaudeSession:
    def __init__(self, claude, transcriber, home):
        self._claude = claude
        self._transcriber = transcriber
        self._home = home

    def run(self, *, prompt, working_dir, transcript_path):
        sid = str(uuid.uuid4())
        result = self._claude(prompt, workspace=working_dir, session_id=sid)
        encoded_cwd = "-" + str(working_dir).strip("/").replace("/", "-").replace("_", "-")
        jsonl_path = self._home / ".claude" / "projects" / encoded_cwd / f"{sid}.jsonl"
        self._transcriber(jsonl_path, transcript_path)
        return result
