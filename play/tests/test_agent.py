from pathlib import Path
from unittest.mock import ANY, MagicMock

import pytest

from agent import Agent
from claude_session import ClaudeSession

_TASK_NAME = "my-task"


class TestAgent:
    @pytest.fixture
    def tasks_root(self, tmp_path):
        root = tmp_path / "tasks"
        root.mkdir()
        return root

    @pytest.fixture
    def create_test_task_with(self, tasks_root):
        def make(prompt="do the thing", name=_TASK_NAME):
            task = tasks_root / name
            task.mkdir()
            (task / "TASK.md").write_text(prompt)
        return make

    @pytest.fixture
    def session_spy(self):
        return MagicMock(spec=ClaudeSession)

    def test_should_call_claude_session_and_make_transcript_available(self, tasks_root, create_test_task_with, session_spy):
        task_prompt = "do the thing"
        working_dir = Path("/work")
        transcript_path = working_dir / "transcript.md"
        create_test_task_with(prompt=task_prompt, name=_TASK_NAME)

        agent = Agent(
            tasks_root=tasks_root,
            session=session_spy,
        )
        agent.perform(
            task=_TASK_NAME,
            working_dir=working_dir,
        )

        assert agent.transcript == transcript_path
        session_spy.run.assert_called_once_with(
            prompt=task_prompt,
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

    def test_transcript_location_should_be_exposed(self, tasks_root, create_test_task_with, session_spy):
        create_test_task_with("dummy prompt")
        working_dir = "/other/dir"

        agent = Agent(
            tasks_root=tasks_root,
            session=session_spy,
        )

        agent.perform(
            working_dir=Path(working_dir),
            task=_TASK_NAME,
        )

        assert agent.transcript == Path(working_dir) / "transcript.md"

    class TestCallsSession:
        def test_prompt_should_be_read_from_task_file(self, tasks_root, create_test_task_with, dummy, session_spy):
            task_prompt = "do the other thing"
            create_test_task_with(task_prompt)

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                task=_TASK_NAME, working_dir=dummy,
            )

            session_spy.run.assert_called_once_with(
                prompt=task_prompt,
                working_dir=ANY, transcript_path=ANY,
            )

        def test_prompt_should_be_read_from_the_named_task(self, tasks_root, create_test_task_with, dummy, session_spy):
            task_name = "another-task"
            task_prompt = "the prompt"
            create_test_task_with(prompt=task_prompt, name=task_name)

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                task=task_name,
                working_dir=dummy,
            )

            session_spy.run.assert_called_once_with(
                prompt=task_prompt,
                working_dir=ANY, transcript_path=ANY,
            )

        def test_working_dir_should_be_passed_to_session(self, tasks_root, create_test_task_with, session_spy):
            create_test_task_with("dummy prompt")

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                working_dir=Path("/other/dir"),
                task=_TASK_NAME,
            )

            session_spy.run.assert_called_once_with(
                working_dir=Path("/other/dir"),
                prompt=ANY, transcript_path=ANY,
            )

        def test_transcript_path_should_be_inside_working_dir(self, tasks_root, create_test_task_with, session_spy):
            create_test_task_with("dummy prompt")

            Agent(
                tasks_root=tasks_root,
                session=session_spy,
            ).perform(
                working_dir=Path("/other/dir"),
                task=_TASK_NAME,
            )

            session_spy.run.assert_called_once_with(
                transcript_path=Path("/other/dir") / "transcript.md",
                prompt=ANY, working_dir=ANY,
            )
