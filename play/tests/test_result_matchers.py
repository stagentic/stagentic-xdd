import pytest
from hamcrest import assert_that

from result import Failure, Success
from result_matchers import is_a_success


class TestIsASuccess:
    def test_should_match_a_success(self):
        result = Success("anything")
        assert_that(result, is_a_success())

    def test_should_raise_when_the_result_is_a_failure(self):
        with pytest.raises(AssertionError):
            assert_that(Failure("the failures"), is_a_success())
