from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agent import Agent
from claude_session import ClaudeSession
from test_doubles.spy_interrogation import value_passed_to


class TestAgent:
    @pytest.fixture
    def workspace(self, tmp_path):
        tasks = tmp_path / "tasks"
        (tasks / "my-task").mkdir(parents=True)
        (tasks / "my-task" / "TASK.md").write_text("do the thing")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()
        return SimpleNamespace(
            tasks=tasks,
            working_dir=working_dir
        )

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
        session_spy = MagicMock()

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
    def test_working_dir_should_be_passed_to_session(self, supplied_working_dir, workspace, dummy):
        session_spy = MagicMock()

        Agent(tasks=workspace.tasks, session=session_spy).perform(
            task="my-task",
            working_dir=supplied_working_dir
        )

        assert value_passed_to(session_spy.run, "working_dir") == supplied_working_dir

    def test_transcript_path_should_be_inside_working_dir(self, workspace, dummy):
        session_spy = MagicMock()

        Agent(tasks=workspace.tasks, session=session_spy).perform(
            task="my-task",
            working_dir=workspace.working_dir
        )

        assert value_passed_to(session_spy.run, "transcript_path") == workspace.working_dir / "transcript.md"

    def test_perform_reads_task_and_delegates_to_session(self, workspace, tmp_path):
        claude_spy = MagicMock(return_value="")
        transcriber_spy = MagicMock()

        session = ClaudeSession(
            claude=claude_spy,
            transcriber=transcriber_spy,
            home=tmp_path / "home"
        )
        agent = Agent(
            tasks=workspace.tasks,
            session=session
        )

        agent.perform(
            task="my-task",
            working_dir=workspace.working_dir
        )

        assert value_passed_to(transcriber_spy, "output_path") == workspace.working_dir / "transcript.md"
        assert agent.transcript == workspace.working_dir / "transcript.md"

