import pytest


def case(id, **named_value):
    (value,) = named_value.values()
    return pytest.param(value, id=id)
