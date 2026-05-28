from pathlib import Path

from claude_session import ClaudeSession


class TestClaudeSession:
    def test_claude_is_called_transcribes_and_returns_result(self):
        claude_calls = []
        transcriber_calls = []

        working_dir = Path("/work_dir")
        transcript_path = Path("/output/transcript.md")
        result = ClaudeSession(
            claude=_claude_spy(claude_calls, returns="claude said this"),
            transcriber=_transcriber_spy(transcriber_calls),
            home=Path("/some/home"),
        ).run(
            prompt="my prompt",
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

        prompt, kwargs = claude_calls[0]
        assert prompt == "my prompt"
        assert kwargs["workspace"] == working_dir
        assert result == "claude said this"

        jsonl_path, output_path = transcriber_calls[0]
        assert jsonl_path.parent == Path("/some/home/.claude/projects/-work-dir")
        assert jsonl_path.suffix == ".jsonl"
        assert output_path == transcript_path

    def test_each_run_uses_a_unique_session_id(self):
        claude_calls = []

        def capture(prompt, **kwargs):
            claude_calls.append(kwargs["session_id"])
            return ""

        session = ClaudeSession(claude=capture, transcriber=lambda *_: None, home=Path("/h"))
        session.run(prompt="p", working_dir=Path("/w"), transcript_path=Path("/t"))
        session.run(prompt="p", working_dir=Path("/w"), transcript_path=Path("/t"))

        assert claude_calls[0] != claude_calls[1]


def _claude_spy(calls, *, returns=""):
    def spy(prompt, **kwargs):
        calls.append((prompt, kwargs))
        return returns
    return spy


def _transcriber_spy(calls):
    def spy(jsonl_path, output_path):
        calls.append((jsonl_path, output_path))
    return spy
