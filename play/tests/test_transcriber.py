from pathlib import Path

from hamcrest import assert_that, equal_to

from transcriber import Transcriber

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_TRANSCRIPT = FIXTURES / "sample-transcript.jsonl"


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
