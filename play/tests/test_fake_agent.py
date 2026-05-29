from fake_agent import FakeAgent


class TestFakeAgent:
    def test_perform_runs_the_named_task_script_in_the_working_directory(self, tmp_path):
        tasks_root = tmp_path / "tasks"
        task_dir = tasks_root / "leaves-sentinel"
        task_dir.mkdir(parents=True)
        (task_dir / "fake-task.sh").write_text("touch sentinel.txt\n")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()

        FakeAgent(tasks_root=tasks_root).perform(
            task="leaves-sentinel", working_dir=working_dir,
        )

        assert (working_dir / "sentinel.txt").exists()

    def test_transcript_is_the_path_in_the_working_directory_after_perform(self, tmp_path):
        tasks_root = tmp_path / "tasks"
        task_dir = tasks_root / "writes-transcript"
        task_dir.mkdir(parents=True)
        (task_dir / "fake-task.sh").write_text("touch transcript.md\n")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()

        agent = FakeAgent(tasks_root=tasks_root)
        agent.perform(task="writes-transcript", working_dir=working_dir)

        assert agent.transcript == working_dir / "transcript.md"
