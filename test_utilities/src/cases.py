import pytest


def case(id, **named_values):
    return pytest.param(*named_values.values(), id=id)
