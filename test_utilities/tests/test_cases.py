import pytest

from cases import case


class TestCase:
    def test_case_should_pair_the_scenario_name_with_values(self):
        param = case(
            "a scenario name",
            shape="hexagon", size="large"
        )

        assert param.id == "a scenario name"
        assert param.values == ("hexagon", "large")

    @pytest.mark.parametrize(
        "scenario_name",
        [
            "scenario name",
            "a different scenario name",
        ],
    )
    def test_case_should_use_the_scenario_name_as_its_id(self, scenario_name):
        param = case(scenario_name, any="value")

        assert param.id == scenario_name

    def test_case_should_allow_values_to_be_arbitrarily_named(self):
        param = case("scenario name", wave="sine")

        assert param.values == ("sine",)
