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

    @pytest.mark.parametrize("erroneous_items, with_message, expected_message", [
        case(
            "items-in-message",
            ["a", "b"],
            lambda items: f"got {items}", "got ['a', 'b']"
        ),
        case(
            "count-of-items",
            ["x"],
            lambda items: f"count {len(items)}", "count 1"
        ),
    ])
    def test_raises_the_given_error_with_the_formatted_message(
            self, erroneous_items, with_message, expected_message,
    ):
        with pytest.raises(ValueError) as excinfo:
            raise_if(
                erroneous_items,
                raising_error=ValueError,
                with_message=with_message
            )

        assert str(excinfo.value) == expected_message
