import pytest
from test_doubles.stubbed_subprocess import StubbedSubprocess

from claude_cli import ClaudeCli


class TestClaudeCli:
    @pytest.fixture
    def calls(self):
        return []

    def test_submits_full_command_to_subprocess(self, calls, tmp_path):
        ClaudeCli(subprocess=_subprocess_spy(calls))(
            "evaluate this",
            workspace=tmp_path,
            session_id="abc-123"
        )

        cmd, kwargs = calls[0]
        assert "evaluate this" in cmd
        assert "--session-id" in cmd and "abc-123" in cmd
        assert "--add-dir" in cmd and str(tmp_path) in cmd
        assert kwargs["cwd"] == tmp_path

    def test_returns_stdout_when_subprocess_succeeds(self):
        successful = StubbedSubprocess(returncode=0, stdout="PASS\n")

        result = ClaudeCli(subprocess=successful)("any prompt")

        assert result == "PASS\n"

    def test_omits_session_id_from_command_when_not_provided(self, calls):
        ClaudeCli(subprocess=_subprocess_spy(calls))("any prompt")

        cmd, _ = calls[0]
        assert "--session-id" not in cmd

    def test_omits_workspace_from_command_when_not_provided(self, calls):
        ClaudeCli(subprocess=_subprocess_spy(calls))("any prompt")

        cmd, kwargs = calls[0]
        assert "--add-dir" not in cmd
        assert kwargs["cwd"] is None

    def test_raises_RuntimeError_when_subprocess_fails(self):
        failing = StubbedSubprocess(returncode=1, stderr="something went wrong")

        with pytest.raises(RuntimeError):
            ClaudeCli(subprocess=failing)("any prompt")


def _subprocess_spy(calls):
    def spy(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return StubbedSubprocess(returncode=0, stdout="")(cmd)
    return spy
