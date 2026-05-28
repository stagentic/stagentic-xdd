import pytest
from pathlib import Path
from unittest.mock import MagicMock

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from claude_session import ClaudeSession


_DUMMY_PATH = Path("/dummy-path")
_DUMMY = MagicMock()


class TestClaudeSession:
    class TestCallsClaudeCli:
        @pytest.mark.parametrize(
            "supplied_prompt", [
                "my prompt",
                "another prompt"
            ]
        )
        def test_prompt_should_be_passed_to_cli(self, supplied_prompt):
            claude_cli_spy = MagicMock(spec=ClaudeCli)

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=_DUMMY,
                home=_DUMMY_PATH,
            ).run(
                prompt=supplied_prompt,
                working_dir=_DUMMY_PATH,
                transcript_path=_DUMMY_PATH
            )

            received_prompt = _value_passed_to(claude_cli_spy, "prompt")
            assert received_prompt == supplied_prompt

        def test_working_dir_should_be_passed_to_cli(self):
            claude_cli_spy = MagicMock(spec=ClaudeCli)

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=_DUMMY,
                home=_DUMMY_PATH,
            ).run(
                prompt=_DUMMY_PATH,
                working_dir=Path("/work_dir"),
                transcript_path=_DUMMY_PATH
            )

            received_workspace = _value_passed_to(claude_cli_spy, "workspace")
            assert received_workspace == Path("/work_dir")

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


def _value_passed_to(spy, name):
    return spy.call_args.kwargs[name]


def _jsonl_path_passed_to(spy):
    return spy.call_args.args[0]


def _transcript_path_passed_to(spy):
    return spy.call_args.args[1]


def _filename_minus_extension_of(path):
    return Path(path).stem
