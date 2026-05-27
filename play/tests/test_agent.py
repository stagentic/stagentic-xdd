from types import SimpleNamespace

import pytest

from agent import Agent


class TestAgent:
    @pytest.fixture
    def workspace(self, tmp_path):
        tasks = tmp_path / "tasks"
        (tasks / "my-task").mkdir(parents=True)
        (tasks / "my-task" / "TASK.md").write_text("do the thing")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()
        return SimpleNamespace(tasks=tasks, working_dir=working_dir)

    def test_perform_calls_claude_with_the_task_prompt_workspace_and_session_id(self, workspace):
        calls = []

        def spy_claude(prompt, *, workspace, session_id):
            calls.append({"prompt": prompt, "workspace": workspace, "session_id": session_id})

        Agent(tasks=workspace.tasks, claude=spy_claude, transcriber=lambda *_, **__: None).perform(
            task="my-task", working_dir=workspace.working_dir,
        )

        assert calls[0]["prompt"] == "do the thing"
        assert calls[0]["workspace"] == workspace.working_dir
        assert calls[0]["session_id"] is not None

    def test_sid_is_accessible_after_perform(self, workspace):
        agent = Agent(tasks=workspace.tasks, claude=lambda *_, **__: None, transcriber=lambda *_, **__: None)
        agent.perform(task="my-task", working_dir=workspace.working_dir)

        assert agent.sid is not None

    def test_transcriber_receives_jsonl_path_derived_from_cwd_and_sid(self, workspace, tmp_path):
        home = tmp_path / "home"
        received = {}

        def spy_transcriber(jsonl_path, output_path):
            received["jsonl_path"] = jsonl_path

        agent = Agent(
            tasks=workspace.tasks,
            claude=lambda *_, **__: None,
            transcriber=spy_transcriber,
            home=home,
        )
        agent.perform(task="my-task", working_dir=workspace.working_dir)

        encoded_cwd = "-" + str(workspace.working_dir).strip("/").replace("/", "-").replace("_", "-")
        expected = home / ".claude" / "projects" / encoded_cwd / f"{agent.sid}.jsonl"
        assert received["jsonl_path"] == expected

    def test_transcriber_receives_jsonl_path_with_underscores_encoded_as_hyphens(self, tmp_path):
        home = tmp_path / "home"
        tasks = tmp_path / "tasks"
        (tasks / "my-task").mkdir(parents=True)
        (tasks / "my-task" / "TASK.md").write_text("do the thing")
        working_dir = tmp_path / "my_workspace"
        working_dir.mkdir()
        received = {}

        def spy_transcriber(jsonl_path, output_path):
            received["jsonl_path"] = jsonl_path

        agent = Agent(tasks=tasks, claude=lambda *_, **__: None, transcriber=spy_transcriber, home=home)
        agent.perform(task="my-task", working_dir=working_dir)

        assert "-my-workspace" in str(received["jsonl_path"])

    def test_transcript_is_in_the_working_dir_after_perform(self, workspace):
        def fake_transcriber(jsonl_path, output_path):
            output_path.touch()

        agent = Agent(
            tasks=workspace.tasks,
            claude=lambda *_, **__: None,
            transcriber=fake_transcriber,
        )
        agent.perform(task="my-task", working_dir=workspace.working_dir)

        assert agent.transcript.exists()
