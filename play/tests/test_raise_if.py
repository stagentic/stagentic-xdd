from contextlib import nullcontext as does_not_raise

import pytest

from raise_if import raise_if


def case(id, *values):
    return pytest.param(*values, id=id)


class TestRaiseIf:
    def test_does_not_raise_when_there_are_no_items(self):
        no_erroneous_items_to_raise_about = []
        with does_not_raise():
            raise_if(
                no_erroneous_items_to_raise_about,
                raising_error=ValueError,
                with_message=lambda items: "dummy message"
            )

    @pytest.mark.parametrize("raising_error, erroneous_items, with_message, expected_message", [
        case(
            "items-in-message",
            ValueError,
            ["a", "b"],
            lambda items: f"got {items}",
            "got ['a', 'b']"
        ),
        case(
            "assertion-error",
            AssertionError,
            ["x"],
            lambda items: "boom",
            "boom"
        ),
    ])
    def test_raises_the_given_error_with_the_formatted_message(
            self, raising_error, erroneous_items, with_message, expected_message,
    ):
        with pytest.raises(raising_error) as excinfo:
            raise_if(
                erroneous_items,
                raising_error=raising_error,
                with_message=with_message
            )

        assert str(excinfo.value) == expected_message
