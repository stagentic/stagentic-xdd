class Agent:
    def __init__(self, *, tasks, session):
        self._tasks = tasks
        self._session = session

    def perform(self, *, task, working_dir):
        prompt = (self._tasks / task / "TASK.md").read_text()
        self.transcript = working_dir / "transcript.md"
        self._session.run(prompt=prompt, working_dir=working_dir, transcript_path=self.transcript)
