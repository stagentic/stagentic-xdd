from pathlib import Path

from transcriber import Transcriber

FIXTURES = Path(__file__).parent / "fixtures"


class TestTranscriber:
    def test_renders_jsonl_to_markdown(self):
        jsonl_path = FIXTURES / "sample-transcript.jsonl"
        expected = (FIXTURES / "sample-transcript.md").read_text()

        result = Transcriber().render(jsonl_path)

        assert result == expected
