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
