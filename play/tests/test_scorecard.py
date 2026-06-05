from scorecard import formatted_failures_for


class TestFormattedFailures:
    def test_formatted_failures_should_render_every_row_on_its_own_line(self):
        failed_characteristics = [
            {"characteristic": "captures input", "failure": "input not captured"},
            {"characteristic": "returns output", "failure": "no output produced"},
        ]

        assert formatted_failures_for(failed_characteristics) == (
            "- captures input: input not captured\n"
            "- returns output: no output produced"
        )

    def test_formatted_failures_should_render_the_row_characteristic_and_failure(self):
        failed_characteristics = [
            {"characteristic": "handles errors", "failure": "errors not handled"}
        ]

        assert formatted_failures_for(failed_characteristics) == (
            "- handles errors: errors not handled"
        )
