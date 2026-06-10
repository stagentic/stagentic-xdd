from unittest.mock import MagicMock

import pytest
from test_doubles.stubbed_subprocess import StubbedSubprocess

from claude_cli import ClaudeCli


class TestClaudeCli:
    class TestSucceeds:
        def test_should_submit_the_full_command_and_return_stdout(self, tmp_path):
            subprocess = MagicMock(
                side_effect=StubbedSubprocess(
                    returncode=0, stdout="run complete\n"
                )
            )

            result = ClaudeCli(subprocess=subprocess)(
                "evaluate this",
                workspace=tmp_path,
                session_id="abc-123"
            )

            subprocess.assert_called_once_with(
                ["claude", "--permission-mode", "acceptEdits",
                 "--session-id", "abc-123",
                 "--add-dir", str(tmp_path),
                 "-p", "evaluate this"],
                cwd=tmp_path,
                capture_output=True,
                text=True,
            )
            assert result == "run complete\n"

        def test_should_return_stdout(self):
            successful = StubbedSubprocess(
                returncode=0, stdout="PASS\n"
            )

            result = ClaudeCli(subprocess=successful)("any prompt")

            assert result == "PASS\n"

    class TestBuildsCommand:
        @pytest.fixture
        def subprocess_that_succeeds(self):
            return MagicMock(side_effect=StubbedSubprocess(returncode=0))

        def test_should_include_the_prompt(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)("another prompt")

            cmd = subprocess_that_succeeds.call_args.args[0]
            assert "another prompt" in cmd

        def test_should_include_the_session_id(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)(
                "any prompt", session_id="xyz-789"
            )

            cmd = subprocess_that_succeeds.call_args.args[0]
            assert "--session-id" in cmd
            assert "xyz-789" in cmd

        def test_should_omit_the_session_id_when_not_provided(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)("any prompt")

            subprocess_that_succeeds.assert_called_once()
            cmd = subprocess_that_succeeds.call_args.args[0]
            assert "--session-id" not in cmd

        def test_should_pass_the_workspace_as_add_dir_and_cwd(self, tmp_path, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)(
                "any prompt",
                workspace=tmp_path
            )

            cmd = subprocess_that_succeeds.call_args.args[0]
            assert "--add-dir" in cmd
            assert str(tmp_path) in cmd
            assert subprocess_that_succeeds.call_args.kwargs["cwd"] == tmp_path

        def test_should_omit_the_workspace_when_not_provided(self, subprocess_that_succeeds):
            ClaudeCli(subprocess=subprocess_that_succeeds)("any prompt")

            subprocess_that_succeeds.assert_called_once()
            cmd = subprocess_that_succeeds.call_args.args[0]
            kwargs = subprocess_that_succeeds.call_args.kwargs
            assert "--add-dir" not in cmd
            assert kwargs["cwd"] is None

    class TestErrors:
        def test_should_raise_RuntimeError_when_subprocess_fails(self):
            failing = StubbedSubprocess(
                returncode=1, stderr="something went wrong"
            )

            with pytest.raises(RuntimeError, match="something went wrong"):
                ClaudeCli(subprocess=failing)("any prompt")
