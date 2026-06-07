from hamcrest import assert_that
from matchers import contains_strings


class TestContainsStrings:
    def test_matches_text_containing_every_substring(self):
        assert_that("alpha and beta", contains_strings("alpha", "beta"))
