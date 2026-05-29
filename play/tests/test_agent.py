import pytest
from pathlib import Path
from unittest.mock import MagicMock

from agent import Agent
from claude_session import ClaudeSession
from test_doubles.spy_interrogation import value_passed_to


class TestAgent:
    @pytest.fixture
    def make_tasks(self, tmp_path):
        def make(supplied_task_text="do the thing"):
            tasks = tmp_path / "tasks"
            (tasks / "my-task").mkdir(parents=True)
            (tasks / "my-task" / "TASK.md").write_text(supplied_task_text)
            return tasks
        return make

    @pytest.fixture
    def tasks(self, make_tasks):
        return make_tasks()

    class TestCallsSession:
        @pytest.mark.parametrize(
            "supplied_task_text", [
                "do the thing", "another task"
            ],
            ids=["do the thing", "another task"]
        )
        def test_prompt_should_be_read_from_task_file(self, supplied_task_text, make_tasks, dummy):
            session_spy = MagicMock(spec=ClaudeSession)

            Agent(tasks=make_tasks(supplied_task_text), session=session_spy).perform(
                task="my-task",
                working_dir=dummy
            )

            received_prompt = value_passed_to(session_spy.run, "prompt")
            assert received_prompt == supplied_task_text

        @pytest.mark.parametrize(
            "supplied_working_dir", [
                Path("/work"), Path("/other/dir")
            ],
            ids=["/work", "/other/dir"]
        )
        def test_working_dir_should_be_passed_to_session(self, supplied_working_dir, tasks):
            session_spy = MagicMock(spec=ClaudeSession)

            Agent(tasks=tasks, session=session_spy).perform(
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
        def test_transcript_path_should_be_inside_working_dir(self, supplied_working_dir, tasks):
            session_spy = MagicMock(spec=ClaudeSession)

            Agent(tasks=tasks, session=session_spy).perform(
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
        def test_transcript_attribute_should_be_set_after_perform(self, supplied_working_dir, tasks):
            session_spy = MagicMock(spec=ClaudeSession)
            agent = Agent(tasks=tasks, session=session_spy)

            agent.perform(task="my-task", working_dir=supplied_working_dir)

            assert agent.transcript == supplied_working_dir / "transcript.md"
