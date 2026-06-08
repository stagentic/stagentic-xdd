import pytest


def case(id, **named_values):
    return pytest.param("amber", id=id)
