from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agent import Agent
from claude_session import ClaudeSession
from test_doubles.spy_interrogation import value_passed_to


class TestAgent:
    @pytest.fixture
    def tasks(self, tmp_path):
        tasks = tmp_path / "tasks"
        (tasks / "my-task").mkdir(parents=True)
        (tasks / "my-task" / "TASK.md").write_text("do the thing")
        return tasks

    @pytest.mark.parametrize(
        "task_text", [
            "do the thing", "another task"
        ],
        ids=["do the thing", "another task"]
    )
    def test_prompt_should_be_read_from_task_file(self, task_text, tmp_path, dummy):
        tasks = tmp_path / "tasks"
        (tasks / "my-task").mkdir(parents=True)
        (tasks / "my-task" / "TASK.md").write_text(task_text)
        session_spy = MagicMock(spec=ClaudeSession)

        Agent(tasks=tasks, session=session_spy).perform(
            task="my-task",
            working_dir=dummy
        )

        assert value_passed_to(session_spy.run, "prompt") == task_text

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

        assert value_passed_to(session_spy.run, "working_dir") == supplied_working_dir

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

        assert value_passed_to(session_spy.run, "transcript_path") == supplied_working_dir / "transcript.md"

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


