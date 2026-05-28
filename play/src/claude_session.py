import uuid

from claude_jsonl_path import ClaudeJsonlPath


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
