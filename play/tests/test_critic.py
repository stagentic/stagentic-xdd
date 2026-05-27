import json

import pytest

from claude_session import ClaudeSession
from critic import Critic


class TestCritic:
    @pytest.fixture
    def evidence(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    def test_evaluate_builds_prompt_and_delegates_to_session(self, evidence, tmp_path):
        working_dir = tmp_path / "workspace"
        claude_cli_calls = []
        transcriber_calls = []

        session = ClaudeSession(
            claude=_claude_spy(
                claude_cli_calls,
                returns='[{"characteristic": "always passes", "status": "PASS"}]'
            ),
            transcriber=_transcriber_spy(transcriber_calls),
            home=tmp_path / "home",
        )
        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=working_dir,
            should=[{"characteristic": "always passes", "failure": "should never see this"}],
        )

        assert str(evidence) in claude_cli_calls[0]["prompt"]
        assert str(working_dir) in claude_cli_calls[0]["prompt"]
        assert claude_cli_calls[0]["workspace"] == working_dir
        assert transcriber_calls[0] == working_dir / "critique.md"

    def test_evaluate_includes_characteristics_in_prompt(self, evidence, tmp_path):
        claude_cli_calls = []

        session = ClaudeSession(
            claude=_claude_spy(
                claude_cli_calls,
                returns='[{"characteristic": "my characteristic", "status": "PASS"}]',
            ),
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )
        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=tmp_path,
            should=[{"characteristic": "my characteristic", "failure": "x"}],
        )

        assert "my characteristic" in claude_cli_calls[0]["prompt"]

    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, evidence, tmp_path):
        session = ClaudeSession(
            claude=lambda *_, **__: '[{"characteristic": "my characteristic", "status": "FAIL"}]',
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

        with pytest.raises(AssertionError) as excinfo:
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[{"characteristic": "my characteristic", "failure": "my failure message"}],
            )

        assert "my characteristic" in str(excinfo.value)
        assert "my failure message" in str(excinfo.value)

    def test_evaluate_raises_ValueError_when_response_is_not_valid_json(self, evidence, tmp_path):
        session = ClaudeSession(
            claude=lambda *_, **__: "I cannot access those files.",
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

        with pytest.raises(ValueError, match="unaccounted"):
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[{"characteristic": "my characteristic", "failure": "my failure"}],
            )

    def test_evaluate_handles_json_wrapped_in_markdown_code_fence(self, evidence, tmp_path):
        session = ClaudeSession(
            claude=lambda *_, **__: '```json\n[{"characteristic": "always passes", "status": "PASS"}]\n```\n',
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=tmp_path,
            should=[{"characteristic": "always passes", "failure": "should never see this"}],
        )

    def test_failure_message_lists_every_failed_row(self, evidence, tmp_path):
        session = ClaudeSession(
            claude=lambda *_, **__: (
                '[{"characteristic": "first", "status": "FAIL"},'
                ' {"characteristic": "middle", "status": "PASS"},'
                ' {"characteristic": "third", "status": "FAIL"}]'
            ),
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

        with pytest.raises(AssertionError) as excinfo:
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "first", "failure": "first failure"},
                    {"characteristic": "middle", "failure": "middle failure"},
                    {"characteristic": "third", "failure": "third failure"},
                ],
            )

        message = str(excinfo.value)
        assert "first" in message and "first failure" in message
        assert "middle" not in message and "middle failure" not in message
        assert "third" in message and "third failure" in message

    def test_evaluate_chains_underlying_parse_error_as_cause(self, evidence, tmp_path):
        session = ClaudeSession(
            claude=lambda *_, **__: "not json",
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

        with pytest.raises(ValueError) as excinfo:
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[{"characteristic": "x", "failure": "y"}],
            )

        assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)

    def test_evaluate_raises_ValueError_when_characteristic_is_missing_from_response(self, evidence, tmp_path):
        session = ClaudeSession(
            claude=lambda *_, **__: '[{"characteristic": "only this one", "status": "PASS"}]',
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

        with pytest.raises(ValueError, match="unaccounted"):
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "only this one", "failure": "x"},
                    {"characteristic": "missing from response", "failure": "y"},
                ],
            )


def _claude_spy(calls, *, returns):
    def spy(prompt, **kwargs):
        calls.append({"prompt": prompt, "workspace": kwargs["workspace"]})
        return returns
    return spy


def _transcriber_spy(transcribed):
    def spy(_jsonl_path, output_path):
        transcribed.append(output_path)
    return spy
