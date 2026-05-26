import subprocess

import pytest


@pytest.mark.contract
def test_claude_cli_responds_to_a_simple_prompt():
    result = subprocess.run(
        ["claude", "--permission-mode", "acceptEdits", "-p",
         "Respond with exactly the word PASS and nothing else."],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout
