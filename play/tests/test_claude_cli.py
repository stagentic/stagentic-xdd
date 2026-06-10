from unittest.mock import MagicMock

import pytest
from test_doubles.stubbed_subprocess import StubbedSubprocess

from claude_cli import ClaudeCli


class TestClaudeCli:
    class TestSucceeds:
        def test_should_submit_the_full_command(self, tmp_path):
            subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

            ClaudeCli(subprocess=subprocess)(
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

        def test_should_return_stdout(self):
            successful = StubbedSubprocess(returncode=0, stdout="PASS\n")

            result = ClaudeCli(subprocess=successful)("any prompt")

            assert result == "PASS\n"

    class TestBuildsCommand:
        def test_should_include_the_prompt(self):
            subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

            ClaudeCli(subprocess=subprocess)("another prompt")

            cmd = subprocess.call_args.args[0]
            assert "another prompt" in cmd

        def test_should_include_the_session_id(self):
            subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

            ClaudeCli(subprocess=subprocess)("any prompt", session_id="xyz-789")

            cmd = subprocess.call_args.args[0]
            assert "--session-id" in cmd
            assert "xyz-789" in cmd

        def test_should_omit_the_session_id_when_not_provided(self):
            subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

            ClaudeCli(subprocess=subprocess)("any prompt")

            subprocess.assert_called_once()
            cmd = subprocess.call_args.args[0]
            assert "--session-id" not in cmd

        def test_should_pass_the_workspace_as_add_dir_and_cwd(self, tmp_path):
            subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

            ClaudeCli(subprocess=subprocess)("any prompt", workspace=tmp_path)

            cmd = subprocess.call_args.args[0]
            assert "--add-dir" in cmd
            assert str(tmp_path) in cmd
            assert subprocess.call_args.kwargs["cwd"] == tmp_path

        def test_should_omit_the_workspace_when_not_provided(self):
            subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

            ClaudeCli(subprocess=subprocess)("any prompt")

            subprocess.assert_called_once()
            cmd = subprocess.call_args.args[0]
            kwargs = subprocess.call_args.kwargs
            assert "--add-dir" not in cmd
            assert kwargs["cwd"] is None

    class TestErrors:
        def test_should_raise_RuntimeError_when_subprocess_fails(self):
            failing = StubbedSubprocess(returncode=1, stderr="something went wrong")

            with pytest.raises(RuntimeError, match="something went wrong"):
                ClaudeCli(subprocess=failing)("any prompt")
