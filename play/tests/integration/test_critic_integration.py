import pytest

from claude_cli import ClaudeCli
from critic import Critic

_TRANSCRIPT_PYTEST_RAN_AND_FAILED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 passed in 0.01s
"""

@pytest.mark.integration
def test_critic_passes_when_all_characteristics_are_met(tmp_path):
    transcript = tmp_path / "transcript.md"
    transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

    Critic(claude=ClaudeCli()).evaluate(
        evidence=transcript,
        working_dir=tmp_path,
        scorecard=[
            {"characteristic": "Transcript shows the agent ran pytest",
             "failure": "No pytest invocation found in the transcript"},
            {"characteristic": "Transcript shows a PASS pytest result",
             "failure": "No FAILED result found in the transcript"},
        ],
    )

