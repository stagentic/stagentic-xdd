import pytest

from claude_cli import ClaudeCli
from test_doubles.stubbed_subprocess import StubbedSubprocess


class TestClaudeCli:
    def test_raises_RuntimeError_when_subprocess_fails(self):
        failing = StubbedSubprocess(returncode=1, stderr="something went wrong")

        with pytest.raises(RuntimeError):
            ClaudeCli(subprocess=failing)("any prompt")

    def test_returns_stdout_when_subprocess_succeeds(self):
        succeeding = StubbedSubprocess(returncode=0, stdout="PASS\n")

        result = ClaudeCli(subprocess=succeeding)("any prompt")

        assert result == "PASS\n"
