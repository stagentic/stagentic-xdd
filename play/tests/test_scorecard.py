from scorecard import formatted_failures_for


class TestFormattedFailures:
    def test_formatted_failures_should_render_the_row_characteristic_and_failure(self):
        failed_characteristics = [{"characteristic": "captures input", "failure": "input not captured"}]

        assert formatted_failures_for(failed_characteristics) == "- captures input: input not captured"
