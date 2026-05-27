import uuid


class Agent:
    def __init__(self, *, tasks, claude, transcriber):
        self._tasks = tasks
        self._claude = claude
        self._transcriber = transcriber

    def perform(self, *, task, working_dir):
        prompt = (self._tasks / task / "TASK.md").read_text()
        self.sid = str(uuid.uuid4())
        self._claude(prompt, workspace=working_dir, session_id=self.sid)
        self.transcript = working_dir / "transcript.md"
        self._transcriber(None, self.transcript)
