from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.matcher import Matcher

from failure_message import formatted_failures_for
from result import Result, Success


class _IsASuccess(BaseMatcher):
    def _matches(self, item: Result) -> bool:
        return isinstance(item, Success)

    def describe_to(self, description: Description) -> None:
        description.append_text("a Success")

    def describe_mismatch(self, item: Result, mismatch_description: Description) -> None:
        mismatch_description.append_text(formatted_failures_for(item.value))


def is_a_success() -> Matcher:
    return _IsASuccess()
