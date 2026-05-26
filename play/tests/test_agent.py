from agent import Agent


class TestAgent:
    def test_perform_calls_claude_with_the_task_prompt_workspace_and_session_id(self, tmp_path):
        tasks = tmp_path / "tasks"
        task_dir = tasks / "my-task"
        task_dir.mkdir(parents=True)
        (task_dir / "TASK.md").write_text("do the thing")
        working_dir = tmp_path / "workspace"
        working_dir.mkdir()
        calls = []

        def spy_claude(prompt, *, workspace, session_id):
            calls.append({"prompt": prompt, "workspace": workspace, "session_id": session_id})

        Agent(tasks=tasks, claude=spy_claude).perform(
            task="my-task", working_dir=working_dir,
        )

        assert calls[0]["prompt"] == "do the thing"
        assert calls[0]["workspace"] == working_dir
        assert calls[0]["session_id"] is not None
