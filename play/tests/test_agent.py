from types import SimpleNamespace

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
        claude_cli_calls = []
        transcriber_calls = []

        session = ClaudeSession(
            claude=_claude_spy(claude_cli_calls),
            transcriber=_transcriber_spy(transcriber_calls),
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

        assert claude_cli_calls[0]["prompt"] == "do the thing"
        assert claude_cli_calls[0]["workspace"] == workspace.working_dir
        assert transcriber_calls[0] == workspace.working_dir / "transcript.md"
        assert agent.transcript == workspace.working_dir / "transcript.md"


def _claude_spy(calls):
    def spy(prompt, **kwargs):
        calls.append({
            "prompt": prompt,
            "workspace": kwargs["workspace"]
        })
        return ""
    return spy


def _transcriber_spy(transcribed):
    def spy(_jsonl_path, output_path):
        transcribed.append(output_path)
    return spy
