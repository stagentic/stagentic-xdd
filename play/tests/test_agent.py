from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agent import Agent
from claude_session import ClaudeSession


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

        assert _value_passed_to(claude_spy, "prompt") == "do the thing"
        assert _value_passed_to(claude_spy, "workspace") == workspace.working_dir
        assert _value_passed_to(transcriber_spy, "output_path") == workspace.working_dir / "transcript.md"
        assert agent.transcript == workspace.working_dir / "transcript.md"


def _values_passed_to(spy, name):
    return [call.kwargs[name] for call in spy.call_args_list]


def _value_passed_to(spy, name):
    return _values_passed_to(spy, name)[-1]
