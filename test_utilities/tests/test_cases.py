import pytest

from cases import case


class TestCase:
    @pytest.mark.parametrize(
        "scenario_name",
        [
            "scenario name",
            "a different scenario name"
        ],
    )
    def test_case_has_a_scenario_name_as_its_id(self, scenario_name):
        param = case(scenario_name, colour="amber")

        assert param.id == scenario_name
        assert param.values == ("amber",)

    def test_case_has_an_arbitrarily_named_value(self):
        param = case("scenario name", wave="sine")

        assert param.values == ("sine",)
