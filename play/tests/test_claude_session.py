from pathlib import Path

from claude_session import ClaudeSession


class TestClaudeSession:
    def test_claude_is_called_transcribes_and_returns_result(self):
        received = []
        transcriber_calls = []

        def capture(prompt, **kwargs):
            received.append((prompt, kwargs))
            return "claude said this"

        def fake_transcriber(*args, **kwargs):
            transcriber_calls.append((args, kwargs))

        working_dir = Path("/work_dir")
        transcript_path = Path("/output/transcript.md")
        result = ClaudeSession(
            claude=capture,
            transcriber=fake_transcriber,
            home=Path("/some/home"),
        ).run(
            prompt="my prompt",
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

        prompt, kwargs = received[0]
        assert prompt == "my prompt"
        assert kwargs["workspace"] == working_dir
        assert result == "claude said this"

        (jsonl_path, output_path), _ = transcriber_calls[0]
        assert jsonl_path.parent == Path("/some/home/.claude/projects/-work-dir")
        assert jsonl_path.stem == kwargs["session_id"]
        assert jsonl_path.suffix == ".jsonl"
        assert output_path == transcript_path
