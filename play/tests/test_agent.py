import pytest
from pathlib import Path
from unittest.mock import MagicMock, ANY

from agent import Agent
from claude_session import ClaudeSession


class TestAgent:
    @pytest.fixture
    def tasks_root(self, tmp_path):
        root = tmp_path / "tasks"
        root.mkdir()
        return root

    @pytest.fixture
    def create_test_task_with(self, tasks_root):
        def make(prompt="do the thing", name="my-task"):
            task = tasks_root / name
            task.mkdir()
            (task / "TASK.md").write_text(prompt)
        return make

    def test_perform_calls_session_with_the_task_and_exposes_the_transcript(self, tasks_root, create_test_task_with):
        task_content = "do the thing"
        task_name = "my-task"
        working_dir = Path("/work")
        transcript_path = working_dir / "transcript.md"
        session_spy = MagicMock(spec=ClaudeSession)
        create_test_task_with(prompt=task_content, name=task_name)

        agent = Agent(
            tasks_root=tasks_root,
            session=session_spy,
        )
        agent.perform(
            task=task_name,
            working_dir=working_dir,
        )

        session_spy.run.assert_called_once_with(
            prompt=task_content,
            working_dir=working_dir,
            transcript_path=transcript_path,
        )
        assert agent.transcript == transcript_path

    class TestCallsSession:
        @pytest.mark.parametrize(
            "supplied_task_content", [
                "do the thing", "another task"
            ],
            ids=["do the thing", "another task"]
        )
        def test_prompt_should_be_read_from_task_file(self, supplied_task_content, tasks_root, create_test_task_with, dummy):
            session_spy = MagicMock(spec=ClaudeSession)
            create_test_task_with(supplied_task_content)

            Agent(tasks_root=tasks_root, session=session_spy).perform(
                task="my-task",
                working_dir=dummy
            )

            session_spy.run.assert_called_once_with(
                prompt=supplied_task_content,
                working_dir=ANY,
                transcript_path=ANY,
            )

        @pytest.mark.parametrize(
            "supplied_task", [
                "my-task", "another-task"
            ],
            ids=["my-task", "another-task"]
        )
        def test_prompt_should_be_read_from_the_named_task(self, supplied_task, tasks_root, create_test_task_with, dummy):
            session_spy = MagicMock(spec=ClaudeSession)
            create_test_task_with(prompt="the prompt", name=supplied_task)

            Agent(tasks_root=tasks_root, session=session_spy).perform(
                task=supplied_task,
                working_dir=dummy
            )

            session_spy.run.assert_called_once_with(
                prompt="the prompt",
                working_dir=ANY,
                transcript_path=ANY,
            )

        @pytest.mark.parametrize(
            "supplied_working_dir", [
                Path("/work"), Path("/other/dir")
            ],
            ids=["/work", "/other/dir"]
        )
        def test_working_dir_should_be_passed_to_session(self, supplied_working_dir, tasks_root, create_test_task_with):
            session_spy = MagicMock(spec=ClaudeSession)
            create_test_task_with()

            Agent(tasks_root=tasks_root, session=session_spy).perform(
                task="my-task",
                working_dir=supplied_working_dir
            )

            session_spy.run.assert_called_once_with(
                prompt=ANY,
                working_dir=supplied_working_dir,
                transcript_path=ANY,
            )

        @pytest.mark.parametrize(
            "supplied_working_dir", [
                Path("/work"), Path("/other/dir")
            ],
            ids=["/work", "/other/dir"]
        )
        def test_transcript_path_should_be_inside_working_dir(self, supplied_working_dir, tasks_root, create_test_task_with):
            session_spy = MagicMock(spec=ClaudeSession)
            create_test_task_with()

            Agent(tasks_root=tasks_root, session=session_spy).perform(
                task="my-task",
                working_dir=supplied_working_dir
            )

            session_spy.run.assert_called_once_with(
                prompt=ANY,
                working_dir=ANY,
                transcript_path=supplied_working_dir / "transcript.md",
            )

    class TestExposesTranscript:
        @pytest.mark.parametrize(
            "supplied_working_dir", [
                Path("/work"), Path("/other/dir")
            ],
            ids=["/work", "/other/dir"]
        )
        def test_transcript_attribute_should_be_set_after_perform(self, supplied_working_dir, tasks_root, create_test_task_with):
            session_spy = MagicMock(spec=ClaudeSession)
            create_test_task_with()
            agent = Agent(tasks_root=tasks_root, session=session_spy)

            agent.perform(task="my-task", working_dir=supplied_working_dir)

            assert agent.transcript == supplied_working_dir / "transcript.md"
