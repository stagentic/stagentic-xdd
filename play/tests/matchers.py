"""Shared test assertion matchers (see ADR 0011).

`matching` aliases Hamcrest's `match_equality`, which adapts a matcher for use
where a value is compared with `==` — chiefly test-double call assertions such
as `assert_called_once_with`.
"""

from hamcrest import match_equality as matching

__all__ = ["matching"]
