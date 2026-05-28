import uuid


class ClaudeJsonlPath:
    def __init__(self, *, home, working_dir=None):
        self._home = home
        self._working_dir = working_dir

    def __str__(self):
        encoded = "-" + str(self._working_dir).strip("/").replace("/", "-")
        return str(self._home / ".claude" / "projects" / encoded)


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
