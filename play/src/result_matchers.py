from hamcrest.core.base_matcher import BaseMatcher

from result import Success


class _IsASuccess(BaseMatcher):
    def _matches(self, item):
        return isinstance(item, Success)

    def describe_to(self, description):
        ... # Avoid not implemented error


def is_a_success():
    return _IsASuccess()
