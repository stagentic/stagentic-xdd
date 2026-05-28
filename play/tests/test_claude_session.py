import pytest
from pathlib import Path
from unittest.mock import MagicMock

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from claude_session import ClaudeSession


class TestClaudeSession:
    class TestCallsClaudeCli:
        @pytest.fixture
        def dummy(self): return MagicMock()

        @pytest.mark.parametrize(
            "supplied_prompt", [
                "my prompt", "another prompt"
            ],
            ids=["my prompt", "another prompt"]
        )
        def test_prompt_should_be_passed_to_cli(self, supplied_prompt, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli)

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=supplied_prompt,
                working_dir=dummy,
                transcript_path=dummy
            )

            received_prompt = _value_passed_to(claude_cli_spy, "prompt")
            assert received_prompt == supplied_prompt

        def test_session_id_should_be_passed_to_cli(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli)

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=dummy
            )

            assert _value_passed_to(claude_cli_spy, "session_id") is not None

        def test_unique_session_id_should_be_passed_to_cli_on_each_run(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli)
            session = ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            )

            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)
            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)

            ids = [call.kwargs["session_id"] for call in claude_cli_spy.call_args_list]
            assert ids[0] != ids[1]

        @pytest.mark.parametrize(
            "supplied_working_dir", [
                Path("/work_dir"), Path("/another/dir")
            ],
            ids=["/work_dir", "/another/dir"]
        )
        def test_working_dir_should_be_passed_to_cli(self, supplied_working_dir, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli)

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=supplied_working_dir,
                transcript_path=dummy
            )

            received_workspace = _value_passed_to(claude_cli_spy, "workspace")
            assert received_workspace == supplied_working_dir

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

        jsonl_path = _jsonl_path_passed_to(transcriber_spy)
        assert isinstance(jsonl_path, ClaudeJsonlPath)
        assert str(jsonl_path).startswith("/some/home")

        assert "-work-dir/" in str(jsonl_path)
        assert _transcript_path_passed_to(transcriber_spy) == Path("/output/transcript.md")

        embedded_session_id = _filename_minus_extension_of(jsonl_path)
        assert embedded_session_id == claude_cli_spy.call_args.kwargs["session_id"]



def _value_passed_to(spy, name):
    return spy.call_args.kwargs[name]


def _jsonl_path_passed_to(spy):
    return spy.call_args.args[0]


def _transcript_path_passed_to(spy):
    return spy.call_args.args[1]


def _filename_minus_extension_of(path):
    return Path(path).stem
