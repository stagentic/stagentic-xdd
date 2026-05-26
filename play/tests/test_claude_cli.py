import pytest

from claude_cli import ClaudeCli
from test_doubles.stubbed_subprocess import StubbedSubprocess


class TestClaudeCli:
    def test_raises_RuntimeError_when_subprocess_fails(self):
        failing = StubbedSubprocess(returncode=1, stderr="something went wrong")

        with pytest.raises(RuntimeError):
            ClaudeCli(subprocess=failing)("any prompt")
