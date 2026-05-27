import pytest
from test_doubles.stubbed_subprocess import StubbedSubprocess

from claude_cli import ClaudeCli


class TestClaudeCli:
    def test_raises_RuntimeError_when_subprocess_fails(self):
        failing = StubbedSubprocess(returncode=1, stderr="something went wrong")

        with pytest.raises(RuntimeError):
            ClaudeCli(subprocess=failing)("any prompt")

    def test_returns_stdout_when_subprocess_succeeds(self):
        succeeding = StubbedSubprocess(returncode=0, stdout="PASS\n")

        result = ClaudeCli(subprocess=succeeding)("any prompt")

        assert result == "PASS\n"

    def test_passes_prompt_to_subprocess(self):
        received = []

        def capture(cmd, **kwargs):
            received.append(cmd)
            return StubbedSubprocess(returncode=0, stdout="PASS\n")(cmd)

        ClaudeCli(subprocess=capture)("evaluate this transcript")

        assert "evaluate this transcript" in received[0]

    def test_includes_session_id_in_command_when_provided(self):
        received = []

        def capture(cmd, **kwargs):
            received.append(cmd)
            return StubbedSubprocess(returncode=0, stdout="")(cmd)

        ClaudeCli(subprocess=capture)("my prompt", session_id="abc-123")

        assert "--session-id" in received[0]
        assert "abc-123" in received[0]

    def test_includes_add_dir_in_command_when_workspace_provided(self, tmp_path):
        received = []

        def capture(cmd, **kwargs):
            received.append(cmd)
            return StubbedSubprocess(returncode=0, stdout="[]")(cmd)

        ClaudeCli(subprocess=capture)("my prompt", workspace=tmp_path)

        assert "--add-dir" in received[0]
        assert str(tmp_path) in received[0]
