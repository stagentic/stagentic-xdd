from cases import case


class TestCase:
    def test_case_has_an_id_and_an_arbitrarily_named_arg(self):
        param = case("scenario name", colour="amber")

        assert param.id == "scenario name"
        assert param.values == ("amber",)
