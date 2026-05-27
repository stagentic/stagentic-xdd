from pathlib import Path
from types import SimpleNamespace

import pytest

from claude_session import ClaudeSession
from new_agent import NewAgent


class TestNewAgent:
    @pytest.fixture
    def workspace(self, tmp_path):
        tasks = tmp_path / "tasks"
        (tasks / "my-task").mkdir(parents=True)
        (tasks / "my-task" / "TASK.md").write_text("do the thing")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()
        return SimpleNamespace(tasks=tasks, working_dir=working_dir)

    def test_perform_reads_task_and_delegates_to_session(self, workspace, tmp_path):
        calls = []
        transcribed = []

        def capture(prompt, **kwargs):
            calls.append({"prompt": prompt, "workspace": kwargs["workspace"]})
            return ""

        def capture_transcriber(jsonl_path, output_path):
            transcribed.append(output_path)

        session = ClaudeSession(claude=capture, transcriber=capture_transcriber, home=tmp_path / "home")
        agent = NewAgent(tasks=workspace.tasks, session=session)
        agent.perform(task="my-task", working_dir=workspace.working_dir)

        assert calls[0]["prompt"] == "do the thing"
        assert calls[0]["workspace"] == workspace.working_dir
        assert transcribed[0] == workspace.working_dir / "transcript.md"
        assert agent.transcript == workspace.working_dir / "transcript.md"
