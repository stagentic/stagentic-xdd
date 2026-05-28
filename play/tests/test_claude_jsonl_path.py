from pathlib import Path

from claude_jsonl_path import ClaudeJsonlPath

_DUMMY_SESSION_ID = "sid"
_DUMMY_PATH = Path("/dummy-path")


class TestClaudeJsonlPath:
    def test_path_should_be_rooted_at_a_specified_home(self):
        path = ClaudeJsonlPath(
            home=Path("/some/home"),
            working_dir=_DUMMY_PATH,
            session_id=_DUMMY_SESSION_ID
        )

        assert str(path).startswith("/some/home")

    def test_path_should_be_rooted_at_any_specified_home(self):
        path = ClaudeJsonlPath(
            home=Path("/another/home"),
            working_dir=_DUMMY_PATH,
            session_id=_DUMMY_SESSION_ID
        )

        assert str(path).startswith("/another/home")

    def test_path_should_be_under_claude_projects(self):
        path = ClaudeJsonlPath(
            home=Path("/some/home"),
            working_dir=_DUMMY_PATH,
            session_id=_DUMMY_SESSION_ID
        )

        assert str(path).startswith("/some/home/.claude/projects")

    def test_path_should_encode_working_dir_slashes_as_hyphens(self):
        path = ClaudeJsonlPath(
            home=_DUMMY_PATH,
            working_dir=Path("/foo/bar"),
            session_id=_DUMMY_SESSION_ID
        )

        assert str(path).endswith(f"-foo-bar/{_DUMMY_SESSION_ID}.jsonl")

    def test_path_should_encode_any_working_dir_slashes_as_hyphens(self):
        path = ClaudeJsonlPath(
            home=_DUMMY_PATH,
            working_dir=Path("/workspace/projectx"),
            session_id=_DUMMY_SESSION_ID
        )

        assert str(path).endswith(f"-workspace-projectx/{_DUMMY_SESSION_ID}.jsonl")

    def test_path_should_encode_working_dir_underscores_as_hyphens(self):
        path = ClaudeJsonlPath(
            home=_DUMMY_PATH,
            working_dir=Path("/work_dir"),
            session_id=_DUMMY_SESSION_ID
        )

        assert str(path).endswith(f"-work-dir/{_DUMMY_SESSION_ID}.jsonl")

    def test_path_should_use_session_id_as_filename(self):
        path = ClaudeJsonlPath(
            home=_DUMMY_PATH,
            working_dir=_DUMMY_PATH,
            session_id="abc-123"
        )

        assert str(path).endswith("abc-123.jsonl")

    def test_path_should_be_usable_as_a_filesystem_path(self):
        path = ClaudeJsonlPath(
            home=Path("/some/home"),
            working_dir=Path("/work_dir"),
            session_id=_DUMMY_SESSION_ID
        )

        assert Path(path) == Path(
            f"/some/home/.claude/projects/-work-dir/{_DUMMY_SESSION_ID}.jsonl"
        )
