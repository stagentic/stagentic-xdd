from pathlib import Path

from claude_session import ClaudeSession, ClaudeJsonlPath


class TestClaudeSession:
    def test_claude_is_called_transcribes_and_returns_result(self):
        transcriber_calls = []

        working_dir = Path("/work_dir")
        transcript_path = Path("/output/transcript.md")
        result = ClaudeSession(
            claude=_claude_spy(returns=lambda p, w: f"claude received {p} for {w} and did its work"),
            transcriber=_transcriber_spy(transcriber_calls),
            home=Path("/some/home"),
        ).run(
            prompt="my prompt",
            working_dir=working_dir,
            transcript_path=transcript_path,
        )

        assert result == f"claude received my prompt for {working_dir} and did its work"

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


class TestClaudeJsonlPath:
    def test_path_should_be_rooted_at_a_specified_home(self):
        path = ClaudeJsonlPath(home=Path("/some/home"))
        assert str(path).startswith("/some/home")

    def test_path_should_be_rooted_at_any_specified_home(self):
        path = ClaudeJsonlPath(home=Path("/another/home"))
        assert str(path).startswith("/another/home")

    def test_path_should_be_under_claude_projects(self):
        path = ClaudeJsonlPath(home=Path("/some/home"))
        assert str(path).startswith("/some/home/.claude/projects")


def _claude_spy(*, returns=lambda p,w: ""):
    def spy(prompt, **kwargs):
        return returns(prompt, kwargs["workspace"])
    return spy


def _transcriber_spy(calls):
    def spy(jsonl_path, output_path):
        calls.append((jsonl_path, output_path))
    return spy
