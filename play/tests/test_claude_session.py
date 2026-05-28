from pathlib import Path
from unittest.mock import MagicMock

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from claude_session import ClaudeSession


class TestClaudeSession:
    def test_claude_is_called_transcribes_and_returns_result(self):
        transcriber_spy = MagicMock()
        claude_cli_spy = MagicMock(
            spec=ClaudeCli,
            return_value=f"claude received my prompt for {Path('/work_dir')} and did its work"
        )

        result = ClaudeSession(
            claude=claude_cli_spy,
            transcriber=transcriber_spy,
            home=Path("/some/home"),
        ).run(
            prompt="my prompt",
            working_dir=Path("/work_dir"),
            transcript_path=Path("/output/transcript.md")
        )

        assert result == f"claude received my prompt for {Path('/work_dir')} and did its work"
        assert isinstance(transcriber_spy.call_args.args[0], ClaudeJsonlPath)
        assert transcriber_spy.call_args.args[1] == Path("/output/transcript.md")

    def test_each_run_uses_a_unique_session_id(self):
        claude_cli_spy = MagicMock(spec=ClaudeCli)
        dummy_transcriber = MagicMock()
        session = ClaudeSession(
            claude=claude_cli_spy,
            transcriber=dummy_transcriber,
            home=Path("/h")
        )

        session.run(prompt="p", working_dir=Path("/w"), transcript_path=Path("/t"))
        session.run(prompt="p", working_dir=Path("/w"), transcript_path=Path("/t"))

        ids = [call.kwargs["session_id"] for call in claude_cli_spy.call_args_list]
        assert ids[0] != ids[1]
