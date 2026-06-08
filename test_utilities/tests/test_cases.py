import pytest

from cases import case


class TestCase:
    @pytest.mark.parametrize(
        "scenario_id",
        [
            "scenario name",
            "a different scenario name"
        ],
    )
    def test_case_has_an_id_and_an_arbitrarily_named_arg(self, scenario_id):
        param = case(scenario_id, colour="amber")

        assert param.id == scenario_id
        assert param.values == ("amber",)
