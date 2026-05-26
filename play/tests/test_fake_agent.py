from fake_agent import FakeAgent


class TestFakeAgent:
    def test_perform_runs_the_named_task_script_in_the_working_directory(self, tmp_path):
        tasks = tmp_path / "tasks"
        tasks.mkdir()
        (tasks / "leaves-sentinel.sh").write_text("touch sentinel.txt\n")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()

        FakeAgent(tasks=tasks).perform(
            task="leaves-sentinel", working_dir=working_dir,
        )

        assert (working_dir / "sentinel.txt").exists()

    def test_transcript_is_the_path_in_the_working_directory_after_perform(self, tmp_path):
        tasks = tmp_path / "tasks"
        tasks.mkdir()
        (tasks / "writes-transcript.sh").write_text("touch transcript.md\n")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()

        agent = FakeAgent(tasks=tasks)
        agent.perform(task="writes-transcript", working_dir=working_dir)

        assert agent.transcript == working_dir / "transcript.md"
