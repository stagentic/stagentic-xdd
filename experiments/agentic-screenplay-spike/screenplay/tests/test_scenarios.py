"""TDAB scenarios as pytest tests, Screenplay-style.

One test, four configurations (see tests/fixtures/config.py):
  - real_claude__critic:   real Claude agent, LLM critic judges
  - real_claude__auditor:  real Claude agent, code auditor checks
  - stubbed__critic:       stubbed agent, LLM critic judges canned content
  - stubbed__auditor:      stubbed agent, code auditor checks canned content

The stubbed configs are fast and deterministic; the real-Claude configs are
slow (~30s each) and non-deterministic - keep behind the `integration` mark.
"""
import pytest

from screenplay_core import when
from stagentic_play import then
from tasks import run_decisions_demo_with_one_option, seek_help_deciding
from expectations import the_right_answer_by_skipping_weighing, complete_its_workflow


@pytest.mark.integration
def test_skips_weighing_when_only_one_option_given(decision_support_agent, inspector):
    when(decision_support_agent).attempts_to(run_decisions_demo_with_one_option)

    then(decision_support_agent).should(
        the_right_answer_by_skipping_weighing(witnessed_by=inspector)
    )


@pytest.mark.integration
def test_skips_weighing_when_only_one_option_given__inline_data(
        decision_support_agent,
        inspector,
):
    when(decision_support_agent).attempts_to(seek_help_deciding(
            from_options=[
                "pizza"
            ]
        )
    )

    then(decision_support_agent).should(
        complete_its_workflow(
            as_follows=[
                ("Agent", r"What are you choosing between\?"),
                ("User",  r"pizza"),
                ("Agent", r"Looks like you only gave me one option"),
                ("Agent", r"the (choice|decision) (is|has been) (already )?made"),
            ],
            witnessed_by=inspector,
        )
    )


@pytest.mark.integration
@pytest.mark.configs("stubbed__critic", "stubbed__auditor")
def test_skips_weighing_when_only_one_option_given__stub_only(
        decision_support_agent,
        inspector,
):
    """Example of @pytest.mark.configs: runs only in stubbed configurations.
    Useful for fast feedback during development, or for tests that depend
    on properties only stubbed runs can guarantee (e.g. exact transcript
    content)."""
    when(decision_support_agent).attempts_to(run_decisions_demo_with_one_option)

    then(decision_support_agent).should(
        the_right_answer_by_skipping_weighing(witnessed_by=inspector)
    )
