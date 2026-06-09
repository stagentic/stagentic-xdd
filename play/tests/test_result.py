from pathlib import Path

from hamcrest import assert_that, equal_to

from result import Success


class TestSuccess:
    def test_should_carry_its_value(self):
        transcript = Path("/work/transcript.md")
        assert_that(Success(transcript).value, equal_to(transcript))
