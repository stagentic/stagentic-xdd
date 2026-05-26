import pytest

from claude_cli import ClaudeCli
from critic import Critic

_TRANSCRIPT_PYTEST_RAN_AND_PASSED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 passed in 0.01s
"""

_TRANSCRIPT_PYTEST_RAN_AND_FAILED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 failed in 0.01s
"""


@pytest.mark.integration
def test_critic_passes_when_all_characteristics_are_met(tmp_path):
    transcript = tmp_path / "transcript.md"
    transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_PASSED)

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


@pytest.mark.integration
def test_critic_raises_when_characteristics_are_not_met(tmp_path):
    transcript = tmp_path / "transcript.md"
    transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

    with pytest.raises(AssertionError) as excinfo:
        Critic(claude=ClaudeCli()).evaluate(
            evidence=transcript,
            working_dir=tmp_path,
            scorecard=[
                {"characteristic": "Transcript shows the agent ran pytest",
                 "failure": "No pytest invocation found in the transcript"},
                {"characteristic": "Transcript shows a PASS pytest result",
                 "failure": "No PASS result found in the transcript"},
            ],
        )

    message = str(excinfo.value)
    assert "Transcript shows the agent ran pytest" not in message
    assert "No pytest invocation found in the transcript" not in message

    assert "Transcript shows a PASS pytest result" in message
    assert "No PASS result found in the transcript" in message
