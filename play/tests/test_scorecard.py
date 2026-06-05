import pytest

from scorecard import formatted_failures_for


def case(id, *values):
    return pytest.param(*values, id=id)


class TestFormattedFailures:
    @pytest.mark.parametrize("failed_characteristics, expected", [
        case("captures-input",
             [{"characteristic": "captures input", "failure": "input not captured"}],
             "- captures input: input not captured"),
        case("returns-output",
             [{"characteristic": "returns output", "failure": "no output produced"}],
             "- returns output: no output produced"),
    ])
    def test_formatted_failures_should_render_the_row_characteristic_and_failure(
            self, failed_characteristics, expected):
        assert formatted_failures_for(failed_characteristics) == expected
