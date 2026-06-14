from pathlib import Path
from unittest.mock import MagicMock

from hamcrest import assert_that, equal_to

from claude_jsonl_path import ClaudeJsonlPath
from transcriber import Transcriber

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_TRANSCRIPT = MagicMock(spec=ClaudeJsonlPath)
SAMPLE_TRANSCRIPT.__fspath__.return_value = str(FIXTURES / "sample-transcript.jsonl")


class TestTranscriber:
    def test_should_write_rendered_content_to_the_output_path(self, tmp_path):
        output_path = tmp_path / "transcript.md"
        expected = Transcriber().render(SAMPLE_TRANSCRIPT)

        Transcriber()(jsonl_path=SAMPLE_TRANSCRIPT, output_path=output_path)

        assert_that(output_path.read_text(), equal_to(expected))

    def test_should_render_jsonl_to_markdown(self):
        expected = (FIXTURES / "sample-transcript.md").read_text()

        result = Transcriber().render(SAMPLE_TRANSCRIPT)

        assert_that(result, equal_to(expected))
