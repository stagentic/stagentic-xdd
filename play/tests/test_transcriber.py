from pathlib import Path

from transcriber import Transcriber

FIXTURES = Path(__file__).parent / "fixtures"


class TestTranscriber:
    def test_callable_writes_rendered_content_to_output_path(self, tmp_path):
        jsonl_path = FIXTURES / "sample-transcript.jsonl"
        output_path = tmp_path / "transcript.md"
        expected = Transcriber().render(jsonl_path)

        Transcriber()(jsonl_path, output_path)

        assert output_path.read_text() == expected

    def test_renders_jsonl_to_markdown(self):
        jsonl_path = FIXTURES / "sample-transcript.jsonl"
        expected = (FIXTURES / "sample-transcript.md").read_text()

        result = Transcriber().render(jsonl_path)

        assert result == expected
