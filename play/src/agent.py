import uuid


class Agent:
    def __init__(self, *, tasks, claude, transcriber, home=None):
        self._tasks = tasks
        self._claude = claude
        self._transcriber = transcriber
        self._home = home

    def perform(self, *, task, working_dir):
        prompt = (self._tasks / task / "TASK.md").read_text()
        self.sid = str(uuid.uuid4())
        self._claude(prompt, workspace=working_dir, session_id=self.sid)
        self.transcript = working_dir / "transcript.md"
        encoded_cwd = "-" + str(working_dir).strip("/").replace("/", "-").replace("_", "-")
        jsonl_path = (
            self._home / ".claude" / "projects" / encoded_cwd / f"{self.sid}.jsonl"
            if self._home is not None else None
        )
        self._transcriber(jsonl_path, self.transcript)
