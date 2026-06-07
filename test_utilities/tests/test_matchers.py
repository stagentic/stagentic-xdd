import pytest
from hamcrest import assert_that, equal_to

from matchers import contains_strings


class TestContainsStrings:
    def test_matches_text_containing_every_substring(self):
        assert_that("alpha and beta", contains_strings("alpha", "beta"))

    def test_does_not_match_when_a_substring_is_missing(self):
        with pytest.raises(AssertionError) as excinfo:
            assert_that("only alpha", contains_strings("alpha", "beta"))
        assert_that(str(excinfo.value), equal_to(
            "\nExpected: a string containing 'beta'\n"
            "     but: was 'only alpha'\n"
        ))
