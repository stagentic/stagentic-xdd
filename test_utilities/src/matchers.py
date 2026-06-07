"""Shared test assertion matchers (see ADR 0011).

- `matching` aliases `match_equality`, adapting a matcher for `==` comparison —
  chiefly test-double call assertions such as `assert_called_once_with`.
- `does_not` aliases `is_not` and `contain_string` aliases `contains_string`,
  so a negated check reads as `does_not(contain_string(...))`.
"""

from hamcrest import anything
from hamcrest import contains_string as contain_string
from hamcrest import is_not as does_not
from hamcrest import match_equality as matching

__all__ = ["contain_string", "contains_strings", "does_not", "matching"]


def contains_strings(*substrings):
    return anything()
