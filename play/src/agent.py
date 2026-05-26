import uuid


class Agent:
    def __init__(self, *, tasks, claude):
        self._tasks = tasks
        self._claude = claude

    def perform(self, *, task, working_dir):
        prompt = (self._tasks / task / "TASK.md").read_text()
        self._claude(prompt, workspace=working_dir, session_id=str(uuid.uuid4()))
