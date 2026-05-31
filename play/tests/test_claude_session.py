import pytest
from pathlib import Path
from unittest.mock import MagicMock, ANY, patch

from claude_cli import ClaudeCli
from claude_jsonl_path import ClaudeJsonlPath
from claude_session import ClaudeSession
from transcriber import Transcriber

_FAKE_SESSION_ID = "fake-sid"


class TestClaudeSession:
    @pytest.fixture
    def dummy_path(self): return Path("/dummy")

    @patch("claude_session.uuid.uuid4", return_value=_FAKE_SESSION_ID)
    def test_run_calls_cli_and_transcriber_and_returns_the_cli_result(self, _uuid):
        prompt = "my prompt"
        working_dir = Path("/some_work_dir")
        claude_home = Path("/some/claude_home")
        transcript_path = Path("/output/transcript.md")
        cli_result = "cli result"

        claude_spy = MagicMock(spec=ClaudeCli(), return_value=cli_result)
        transcriber_spy = MagicMock(spec=Transcriber())

        result = ClaudeSession(
            claude=claude_spy,
            transcriber=transcriber_spy,
            home=claude_home,
        ).run(
            prompt=prompt,
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

        claude_spy.assert_called_once_with(
            prompt=prompt,
            workspace=working_dir,
            session_id=_FAKE_SESSION_ID,
        )
        expected_jsonl_path = ClaudeJsonlPath(
            home=claude_home,
            working_dir=working_dir,
            session_id=_FAKE_SESSION_ID,
        )
        transcriber_spy.assert_called_once_with(
            jsonl_path=expected_jsonl_path,
            output_path=transcript_path,
        )
        assert result == cli_result

    class TestCallsClaudeCli:
        def test_prompt_should_be_passed_to_cli(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt="another prompt",
                working_dir=dummy,
                transcript_path=dummy
            )

            claude_cli_spy.assert_called_once_with(
                prompt="another prompt",
                workspace=ANY,
                session_id=ANY,
            )

        def test_working_dir_should_be_passed_to_cli(self, dummy):
            claude_cli_spy = MagicMock(spec=ClaudeCli())

            ClaudeSession(
                claude=claude_cli_spy,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=Path("/another/dir"),
                transcript_path=dummy
            )

            claude_cli_spy.assert_called_once_with(
                prompt=ANY,
                workspace=Path("/another/dir"),
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

        def test_result_from_cli_should_be_returned(self, dummy):
            claude_cli_stub = MagicMock(spec=ClaudeCli(), return_value="another cli result")

            result = ClaudeSession(
                claude=claude_cli_stub,
                transcriber=dummy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=dummy
            )

            assert result == "another cli result"

    class TestCallsTranscriber:
        @pytest.fixture
        def dummy_path(self): return Path("/dummy")

        def test_jsonl_path_should_encode_the_home(self, dummy):
            transcriber_spy = MagicMock()

            ClaudeSession(
                claude=dummy,
                transcriber=transcriber_spy,
                home=Path("/another/home"),
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=dummy
            )

            transcriber_spy.assert_called_once()
            received_jsonl_path = str(transcriber_spy.call_args.kwargs["jsonl_path"])
            assert received_jsonl_path.startswith("/another/home")

        def test_jsonl_path_should_encode_the_working_dir(self, dummy, dummy_path):
            transcriber_spy = MagicMock()

            ClaudeSession(
                claude=dummy,
                transcriber=transcriber_spy,
                home=dummy_path,
            ).run(
                prompt=dummy,
                working_dir=Path("/another/dir"),
                transcript_path=dummy
            )

            transcriber_spy.assert_called_once()
            received_jsonl_path = str(transcriber_spy.call_args.kwargs["jsonl_path"])
            assert "-another-dir/" in received_jsonl_path

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

        def test_transcriber_should_receive_the_transcript_path(self, dummy):
            transcriber_spy = MagicMock()

            ClaudeSession(
                claude=dummy,
                transcriber=transcriber_spy,
                home=dummy,
            ).run(
                prompt=dummy,
                working_dir=dummy,
                transcript_path=Path("/another/output.md")
            )

            transcriber_spy.assert_called_once_with(
                jsonl_path=ANY,
                output_path=Path("/another/output.md"),
            )


def _filename_minus_extension_from(path):
    return Path(path).stem
