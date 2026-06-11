import uuid

import pytest

from claude_cli import ClaudeCli


@pytest.mark.contract
class TestClaudeCliContract:
    def test_should_respond_to_a_simple_prompt(self, tmp_path):
        result = ClaudeCli()(
            "Respond with exactly the word PASS and nothing else.",
            workspace=tmp_path,
            session_id=str(uuid.uuid4()),
        )
        assert "PASS" in result
