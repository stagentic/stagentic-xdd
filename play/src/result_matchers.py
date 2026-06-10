from hamcrest.core.base_matcher import BaseMatcher

from result import Success


class _IsASuccess(BaseMatcher):
    def _matches(self, item):
        return isinstance(item, Success)

    def describe_to(self, description):
        description.append_text("a Success")


def is_a_success():
    return _IsASuccess()
