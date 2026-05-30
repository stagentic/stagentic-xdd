import pytest
from unittest.mock import MagicMock
from test_doubles.stubbed_subprocess import StubbedSubprocess

from claude_cli import ClaudeCli


class TestClaudeCli:
    def test_submits_full_command_to_subprocess(self, tmp_path):
        subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

        ClaudeCli(subprocess=subprocess)(
            "evaluate this",
            workspace=tmp_path,
            session_id="abc-123"
        )

        subprocess.assert_called_once()
        cmd = subprocess.call_args.args[0]
        kwargs = subprocess.call_args.kwargs
        assert "evaluate this" in cmd
        assert "--session-id" in cmd and "abc-123" in cmd
        assert "--add-dir" in cmd and str(tmp_path) in cmd
        assert kwargs["cwd"] == tmp_path

    def test_returns_stdout_when_subprocess_succeeds(self):
        successful = StubbedSubprocess(returncode=0, stdout="PASS\n")

        result = ClaudeCli(subprocess=successful)("any prompt")

        assert result == "PASS\n"

    def test_omits_session_id_from_command_when_not_provided(self):
        subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

        ClaudeCli(subprocess=subprocess)("any prompt")

        subprocess.assert_called_once()
        cmd = subprocess.call_args.args[0]
        assert "--session-id" not in cmd

    def test_omits_workspace_from_command_when_not_provided(self):
        subprocess = MagicMock(side_effect=StubbedSubprocess(returncode=0))

        ClaudeCli(subprocess=subprocess)("any prompt")

        subprocess.assert_called_once()
        cmd = subprocess.call_args.args[0]
        kwargs = subprocess.call_args.kwargs
        assert "--add-dir" not in cmd
        assert kwargs["cwd"] is None

    def test_raises_RuntimeError_when_subprocess_fails(self):
        failing = StubbedSubprocess(returncode=1, stderr="something went wrong")

        with pytest.raises(RuntimeError):
            ClaudeCli(subprocess=failing)("any prompt")
