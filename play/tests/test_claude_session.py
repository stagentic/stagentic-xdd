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
        assert claude_cli_spy.call_args.kwargs["prompt"] == "my prompt"
        assert claude_cli_spy.call_args.kwargs["workspace"] == Path("/work_dir")

        jsonl_path = _jsonl_path_passed_to(transcriber_spy)
        assert isinstance(jsonl_path, ClaudeJsonlPath)
        assert str(jsonl_path).startswith("/some/home")

        assert "-work-dir/" in str(jsonl_path)
        assert _transcript_path_passed_to(transcriber_spy) == Path("/output/transcript.md")

        embedded_session_id = _filename_minus_extension_of(jsonl_path)
        assert embedded_session_id == claude_cli_spy.call_args.kwargs["session_id"]

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


def _jsonl_path_passed_to(spy):
    return spy.call_args.args[0]


def _transcript_path_passed_to(spy):
    return spy.call_args.args[1]


def _filename_minus_extension_of(path):
    return Path(path).stem
