from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.matcher import Matcher

from result import Result, Success


class _IsASuccess(BaseMatcher):
    def _matches(self, item: Result) -> bool:
        return isinstance(item, Success)

    def describe_to(self, description: Description) -> None:
        description.append_text("a Success")


def is_a_success() -> Matcher:
    return _IsASuccess()
