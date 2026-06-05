import pytest

from raise_if import raise_if


class TestRaiseIf:
    def test_raises_the_given_error_with_the_formatted_message(self):
        with pytest.raises(ValueError) as excinfo:
            raise_if(
                ["a", "b"],
                raising_error=ValueError,
                with_message=lambda items: f"got {items}",
            )

        assert str(excinfo.value) == "got ['a', 'b']"
