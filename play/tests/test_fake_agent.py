import pytest

from fake_agent import FakeAgent


class TestFakeAgent:
    @pytest.fixture
    def tasks_root(self, tmp_path):
        root = tmp_path / "tasks"
        root.mkdir()
        return root

    @pytest.fixture
    def working_dir(self, tmp_path):
        path = tmp_path / "workspace"
        path.mkdir()
        return path

    def test_perform_runs_the_named_task_script_in_the_working_directory(self, tasks_root, working_dir):
        task_dir = tasks_root / "leaves-sentinel"
        task_dir.mkdir()
        (task_dir / "fake-task.sh").write_text("touch sentinel.txt\n")

        FakeAgent(tasks_root=tasks_root).perform(
            task="leaves-sentinel", working_dir=working_dir,
        )

        assert (working_dir / "sentinel.txt").exists()

    def test_transcript_is_the_path_in_the_working_directory_after_perform(self, tasks_root, working_dir):
        task_dir = tasks_root / "writes-transcript"
        task_dir.mkdir()
        (task_dir / "fake-task.sh").write_text("touch transcript.md\n")

        agent = FakeAgent(tasks_root=tasks_root)
        agent.perform(task="writes-transcript", working_dir=working_dir)

        assert agent.transcript == working_dir / "transcript.md"
