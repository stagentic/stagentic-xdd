import pytest

from fake_agent import FakeAgent

_TASK_NAME = "my-task"


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
        def make(script, name=_TASK_NAME):
            task = tasks_root / name
            task.mkdir()
            (task / "fake-task.sh").write_text(script)
        return make

    def test_perform_should_run_the_task_script_in_working_dir_and_make_the_transcript_available(self, tasks_root, working_dir, create_test_task_with):
        sentinel_file = "sentinel.txt"
        create_test_task_with(script=f"touch {sentinel_file}\n", name=_TASK_NAME)

        agent = FakeAgent(tasks_root=tasks_root)
        agent.perform(
            task=_TASK_NAME,
            working_dir=working_dir,
        )

        assert (working_dir / sentinel_file).exists()
        assert agent.transcript == working_dir / "transcript.md"

    def test_perform_runs_the_named_task_script_in_the_working_directory(self, tasks_root, working_dir, create_test_task_with):
        task_name = "another-task"
        sentinel_file = "sentinel.txt"
        create_test_task_with(script=f"touch {sentinel_file}\n", name=task_name)

        FakeAgent(tasks_root=tasks_root).perform(
            task=task_name, working_dir=working_dir,
        )

        assert (working_dir / sentinel_file).exists()

    def test_transcript_is_the_path_in_the_working_directory_after_perform(self, tmp_path, tasks_root, create_test_task_with):
        working_dir = tmp_path / "other-workspace"
        working_dir.mkdir()
        create_test_task_with(script="true\n")

        agent = FakeAgent(tasks_root=tasks_root)
        agent.perform(task=_TASK_NAME, working_dir=working_dir)

        assert agent.transcript == working_dir / "transcript.md"
