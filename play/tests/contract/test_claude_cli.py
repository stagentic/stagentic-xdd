import pytest

from claude_cli import ClaudeCli


@pytest.mark.contract
def test_claude_cli_responds_to_a_simple_prompt():
    result = ClaudeCli()("Respond with exactly the word PASS and nothing else.")
    assert "PASS" in result
