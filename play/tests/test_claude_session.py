import pytest
from pathlib import Path
from unittest.mock import MagicMock, ANY

from claude_cli import ClaudeCli
from claude_session import ClaudeSession


class TestClaudeSession:
    class TestCallsClaudeCli:
        @pytest.mark.parametrize(
            "supplied_prompt", [
                "my prompt", "another prompt"
            ],
            ids=["my prompt", "another prompt"]
        )
        def test_prompt_should_be_passed_to_cli(self, supplied_prompt, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=supplied_prompt,
                working_dir=dummy,
                transcript_path=dummy
            )

            claude_cli_spy.assert_called_once_with(
                prompt=supplied_prompt,
                workspace=ANY,
                session_id=ANY,
            )

        @pytest.mark.parametrize(
            "supplied_working_dir", [
                Path("/work_dir"), Path("/another/dir")
            ],
            ids=["/work_dir", "/another/dir"]
        )
        def test_working_dir_should_be_passed_to_cli(self, supplied_working_dir, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=supplied_working_dir,
                transcript_path=dummy
            )

            claude_cli_spy.assert_called_once_with(
                prompt=ANY,
                workspace=supplied_working_dir,
                session_id=ANY,
            )

        def test_unique_session_id_should_be_passed_to_cli_on_each_run(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())
            session = ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            )

            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)
            session.run(prompt=dummy, working_dir=dummy, transcript_path=dummy)

            assert claude_cli_spy.call_count == 2
            first, second = claude_cli_spy.call_args_list
            assert first.kwargs["session_id"] != second.kwargs["session_id"]

        @pytest.mark.parametrize(
            "cli_result", [
                "cli result", "another cli result"
            ],
            ids=["cli result", "another cli result"]
        )
        def test_result_from_cli_should_be_returned(self, cli_result, dummy):
            claude_cli_stub = MagicMock(spec=ClaudeCli(), return_value=cli_result)

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

            transcriber_spy.assert_called_once()
            received_jsonl_path = str(transcriber_spy.call_args.kwargs["jsonl_path"])
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

            transcriber_spy.assert_called_once()
            received_jsonl_path = str(transcriber_spy.call_args.kwargs["jsonl_path"])
            assert expected_fragment in received_jsonl_path

        def test_jsonl_path_should_encode_the_same_session_id_passed_to_cli(self, dummy, dummy_path):
            transcriber_spy = MagicMock()
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=transcriber_spy,
                home=dummy_path,
            ).run(
                prompt=dummy,
                working_dir=dummy_path,
                transcript_path=dummy
            )

            claude_cli_spy.assert_called_once()
            transcriber_spy.assert_called_once()
            session_id_passed_to_cli = claude_cli_spy.call_args.kwargs["session_id"]
            session_id_in_jsonl_path = _filename_minus_extension_from(
                transcriber_spy.call_args.kwargs["jsonl_path"]
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

            transcriber_spy.assert_called_once_with(
                jsonl_path=ANY,
                output_path=supplied_transcript_path,
            )


def _filename_minus_extension_from(path):
    return Path(path).stem
