import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from claude_session import ClaudeSession
from critic import Critic


@dataclass
class _SessionParams:
    claude: Any
    transcriber: Any
    home: Path


class TestCritic:
    @pytest.fixture
    def evidence(self, tmp_path):
        path = tmp_path / "transcript.md"
        path.write_text("anything")
        return path

    @pytest.fixture
    def session_params(self, tmp_path):
        return _SessionParams(
            claude=None,
            transcriber=lambda *_: None,
            home=tmp_path / "home",
        )

    @pytest.fixture
    def _using(self, session_params):
        def factory(**overrides):
            return vars(dataclasses.replace(session_params, **overrides))
        return factory

    def test_evaluate_builds_prompt_and_delegates_to_session(self, evidence, tmp_path, _using):
        working_dir = tmp_path / "workspace"
        claude_cli_calls = []
        transcriber_calls = []

        session = ClaudeSession(**_using(
            claude=_claude_spy(
                claude_cli_calls,
                returns='[{"characteristic": "a characteristic", "status": "PASS"}]'
            ),
            transcriber=_transcriber_spy(transcriber_calls),
        ))

        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=working_dir,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

        assert str(evidence) in claude_cli_calls[0]["prompt"]
        assert str(working_dir) in claude_cli_calls[0]["prompt"]
        assert "a characteristic" in claude_cli_calls[0]["prompt"]
        assert claude_cli_calls[0]["workspace"] == working_dir
        assert transcriber_calls[0] == working_dir / "critique.md"

    def test_evaluate_handles_json_preceded_by_prose(self, evidence, tmp_path, _using):
        prose_then_json = (
            'Based on my evaluation:\n\n'
            '[{"characteristic": "a characteristic", "status": "PASS"}]'
        )
        session = ClaudeSession(**_using(claude=lambda *_, **__: prose_then_json))

        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=tmp_path,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

    def test_evaluate_handles_json_in_code_fence_preceded_by_prose(self, evidence, tmp_path, _using):
        prose_then_fence = (
            'Based on the transcript:\n\n'
            '```json\n[{"characteristic": "a characteristic", "status": "PASS"}]\n```\n'
        )
        session = ClaudeSession(**_using(claude=lambda *_, **__: prose_then_fence))

        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=tmp_path,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

    def test_evaluate_handles_json_wrapped_in_markdown_code_fence(self, evidence, tmp_path, _using):
        markdown = '```json\n[{"characteristic": "a characteristic", "status": "PASS"}]\n```\n'
        session = ClaudeSession(
            **_using(claude=lambda *_, **__: markdown)
        )

        Critic(session=session).evaluate(
            evidence=evidence,
            working_dir=tmp_path,
            should=[{"characteristic": "a characteristic", "failure": "should never see this"}],
        )

    def test_evaluate_raises_with_characteristic_and_failure_when_a_row_fails(self, evidence, tmp_path, _using):
        session = ClaudeSession(**_using(
            claude=lambda *_, **__: '[{"characteristic": "my characteristic", "status": "FAIL"}]'
        ))

        with pytest.raises(AssertionError) as excinfo:
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[{"characteristic": "my characteristic", "failure": "my failure message"}],
            )

        assert "my characteristic" in str(excinfo.value)
        assert "my failure message" in str(excinfo.value)

    def test_failure_message_lists_every_failed_row(self, evidence, tmp_path, _using):
        session = ClaudeSession(**_using(claude=lambda *_, **__: (
            '[{"characteristic": "first", "status": "FAIL"},'
            ' {"characteristic": "middle", "status": "PASS"},'
            ' {"characteristic": "third", "status": "FAIL"}]'
        )))

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

    def test_evaluate_raises_ValueError_with_cause_when_response_is_not_valid_json(self, evidence, tmp_path, _using):
        session = ClaudeSession(**_using(claude=lambda *_, **__: "not valid json."))

        with pytest.raises(ValueError, match="not valid JSON") as excinfo:
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[{"characteristic": "a characteristic", "failure": "my failure"}],
            )

        assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)

    def test_evaluate_raises_ValueError_when_characteristic_is_missing_from_response(self, evidence, tmp_path, _using):
        session = ClaudeSession(**_using(
            claude=lambda *_, **__: '[{"characteristic": "a characteristic", "status": "PASS"}]'
        ))

        with pytest.raises(ValueError, match="unaccounted"):
            Critic(session=session).evaluate(
                evidence=evidence,
                working_dir=tmp_path,
                should=[
                    {"characteristic": "a characteristic", "failure": "x"},
                    {"characteristic": "another characteristic", "failure": "y"},
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
