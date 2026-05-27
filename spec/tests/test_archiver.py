import re

from archiver import archive, current_timestamp


class TestArchiver:
    def test_current_timestamp_format(self):
        assert re.fullmatch(r"\d{8}-\d{6}", current_timestamp())

    def test_archive_copies_workspace_to_timestamped_folder(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "transcript.md").write_text("some content")
        artefacts_dir = tmp_path / "artefacts"
        artefacts_dir.mkdir()

        archive(phase="call", tmp_path=workspace, test_name="test_foo", artefacts_dir=str(artefacts_dir), timestamp="20260527-101638")

        dest = artefacts_dir / "20260527-101638-test_foo"
        assert (dest / "transcript.md").read_text() == "some content"

    def test_archive_does_nothing_outside_call_phase(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        artefacts = tmp_path / "artefacts"
        artefacts.mkdir()

        archive(phase="setup", tmp_path=workspace, test_name="test_foo", artefacts_dir=str(artefacts), timestamp="20260527-101638")

        assert list(artefacts.iterdir()) == []

    def test_archive_does_nothing_when_artefacts_dir_is_not_set(self, tmp_path):
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        artefacts = tmp_path / "artefacts"
        artefacts.mkdir()

        archive(phase="call", tmp_path=workspace, test_name="test_foo", artefacts_dir=None, timestamp="20260527-101638")

        assert list(artefacts.iterdir()) == []
