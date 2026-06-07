from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest
from hamcrest import all_of, assert_that, contains_string
from matchers import contain_string, does_not

from claude_cli import ClaudeCli
from claude_session import ClaudeSession
from critic import Critic
from transcriber import Transcriber

_TRANSCRIPT_PYTEST_RAN_AND_PASSED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 passed in 0.01s
"""

_TRANSCRIPT_PYTEST_RAN_AND_FAILED = """\
[TOOL] **Bash** `uv run pytest tests/`

1 failed in 0.01s
"""


@pytest.mark.integration
class TestCriticIntegration:
    @pytest.fixture
    def session(self):
        return ClaudeSession(
            claude=ClaudeCli(),
            transcriber=Transcriber(),
            home=Path.home(),
        )

    def test_evaluation_should_fail_when_a_characteristic_is_not_met(self, session, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_FAILED)

        with pytest.raises(AssertionError) as excinfo:
            Critic(session=session).evaluate(
                evidence_source=transcript,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "Transcript shows the agent ran pytest",
                     "failure": "No pytest invocation found in the transcript"},
                    {"characteristic": "Transcript shows a PASS pytest result",
                     "failure": "No PASS result found in the transcript"},
                ],
            )

        assert_that(str(excinfo.value), all_of(
            contains_string("Transcript shows a PASS pytest result"),
            contains_string("No PASS result found in the transcript"),
            does_not(contain_string("Transcript shows the agent ran pytest")),
            does_not(contain_string("No pytest invocation found in the transcript")),
        ))

    def test_evaluation_should_pass_when_all_characteristics_are_met(self, session, tmp_path):
        transcript = tmp_path / "transcript.md"
        transcript.write_text(_TRANSCRIPT_PYTEST_RAN_AND_PASSED)

        with does_not_raise():
            Critic(session=session).evaluate(
                evidence_source=transcript,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "Transcript shows the agent ran pytest",
                     "failure": "No pytest invocation found in the transcript"},
                    {"characteristic": "Transcript shows a PASS pytest result",
                     "failure": "No FAILED result found in the transcript"},
                ],
            )
