import pytest
from pathlib import Path
from unittest.mock import MagicMock

from agent import Agent
from claude_session import ClaudeSession
from test_doubles.spy_interrogation import value_passed_to


class TestAgent:
    @pytest.fixture
    def tasks_root(self, tmp_path):
        root = tmp_path / "tasks"
        root.mkdir()
        return root

    @pytest.fixture
    def create_test_task_with(self, tasks_root):
        def make(prompt="do the thing"):
            task = tasks_root / "my-task"
            task.mkdir()
            (task / "TASK.md").write_text(prompt)
        return make

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

            received_prompt = value_passed_to(session_spy.run, "prompt")
            assert received_prompt == supplied_task_content

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

            received_working_dir = value_passed_to(session_spy.run, "working_dir")
            assert received_working_dir == supplied_working_dir

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

            received_transcript_path = value_passed_to(session_spy.run, "transcript_path")
            assert received_transcript_path == supplied_working_dir / "transcript.md"

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
