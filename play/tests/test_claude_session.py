import pytest
from pathlib import Path
from unittest.mock import MagicMock

from claude_cli import ClaudeCli
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

            received_prompt = _value_passed_to(
                claude_cli_spy, "prompt"
            )
            assert received_prompt == supplied_prompt

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

            received_workspace = _value_passed_to(
                claude_cli_spy, "workspace"
            )
            assert received_workspace == supplied_working_dir

        def test_unique_session_id_should_be_passed_to_cli_on_each_run(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli)
            session = ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            )

            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)
            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)

            ids = _values_passed_to(claude_cli_spy, "session_id")
            assert ids[0] != ids[1]

        @pytest.mark.parametrize(
            "cli_result", [
                "cli result", "another cli result"
            ],
            ids=["cli result", "another cli result"]
        )
        def test_result_from_cli_should_be_returned(self, cli_result, dummy):
            claude_cli_stub = MagicMock(spec=ClaudeCli, return_value=cli_result)

            result = ClaudeSession(
                claude=claude_cli_stub,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=dummy
            )

            assert result == cli_result

    class TestCallsTranscriber:
        @pytest.fixture
        def dummy(self): return MagicMock()

        @pytest.fixture
        def dummy_path(self): return Path("/dummy")

        @pytest.mark.parametrize(
            "supplied_home", [
                Path("/some/home"), Path("/another/home")
            ],
            ids=["/some/home", "/another/home"]
        )
        def test_jsonl_path_should_encode_the_home(self, supplied_home, dummy):
            transcriber_spy = MagicMock()

            ClaudeSession(
                claude=dummy,
                transcriber=transcriber_spy,
                home=supplied_home,
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=dummy
            )

            received_jsonl_path = str(_value_passed_to(
                transcriber_spy, "jsonl_path")
            )
            assert received_jsonl_path.startswith(str(supplied_home))

        @pytest.mark.parametrize(
            "supplied_working_dir, expected_fragment", [
                (Path("/work-dir"), "-work-dir/"),
                (Path("/another/dir"), "-another-dir/"),
            ],
            ids=["/work-dir", "/another/dir"]
        )
        def test_jsonl_path_should_encode_the_working_dir(self, supplied_working_dir, expected_fragment, dummy, dummy_path):
            transcriber_spy = MagicMock()

            ClaudeSession(
                claude=dummy,
                transcriber=transcriber_spy,
                home=dummy_path,
            ).run(
                prompt=dummy,
                working_dir=supplied_working_dir,
                transcript_path=dummy
            )

            received_jsonl_path = str(_value_passed_to(transcriber_spy, "jsonl_path"))
            assert expected_fragment in received_jsonl_path

        def test_jsonl_path_should_encode_the_same_session_id_passed_to_cli(self, dummy, dummy_path):
            transcriber_spy = MagicMock()
            claude_cli_spy = MagicMock(spec=ClaudeCli)

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=transcriber_spy,
                home=dummy_path,
            ).run(
                prompt=dummy,
                working_dir=dummy_path,
                transcript_path=dummy
            )

            session_id_passed_to_cli = _value_passed_to(
                claude_cli_spy, "session_id"
            )
            session_id_in_jsonl_path = _filename_minus_extension_of(
                _value_passed_to(transcriber_spy, "jsonl_path")
            )
            assert session_id_in_jsonl_path == session_id_passed_to_cli

        @pytest.mark.parametrize(
            "supplied_transcript_path", [
                Path("/output/transcript.md"), Path("/another/output.md")
            ],
            ids=["/output/transcript.md", "/another/output.md"]
        )
        def test_transcriber_should_receive_the_transcript_path(self, supplied_transcript_path, dummy):
            transcriber_spy = MagicMock()

            ClaudeSession(
                claude=dummy,
                transcriber=transcriber_spy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=supplied_transcript_path
            )

            received_output_path = _value_passed_to(
                transcriber_spy, "output_path"
            )
            assert received_output_path == supplied_transcript_path


def _values_passed_to(spy, name):
    return [call.kwargs[name] for call in spy.call_args_list]


def _value_passed_to(spy, name):
    return _values_passed_to(spy, name)[-1]


def _filename_minus_extension_of(path):
    return Path(path).stem
