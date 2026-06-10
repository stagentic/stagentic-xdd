from hamcrest import assert_that

from result import Success
from result_matchers import is_a_success


class TestIsASuccess:
    def test_should_match_a_success(self):
        result = Success("anything")
        assert_that(result, is_a_success())
