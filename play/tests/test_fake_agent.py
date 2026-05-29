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

    @pytest.fixture
    def create_test_task_with(self, tasks_root):
        def make(script, name="my-task"):
            task = tasks_root / name
            task.mkdir()
            (task / "fake-task.sh").write_text(script)
        return make

    @pytest.mark.parametrize(
        "supplied_task", [
            "my-task", "another-task"
        ],
        ids=["my-task", "another-task"]
    )
    def test_perform_runs_the_named_task_script_in_the_working_directory(self, supplied_task, tasks_root, working_dir, create_test_task_with):
        create_test_task_with("touch sentinel.txt\n", name=supplied_task)

        FakeAgent(tasks_root=tasks_root).perform(
            task=supplied_task, working_dir=working_dir,
        )

        assert (working_dir / "sentinel.txt").exists()

    def test_transcript_is_the_path_in_the_working_directory_after_perform(self, tasks_root, working_dir, create_test_task_with):
        create_test_task_with("true\n")

        agent = FakeAgent(tasks_root=tasks_root)
        agent.perform(task="my-task", working_dir=working_dir)

        assert agent.transcript == working_dir / "transcript.md"
