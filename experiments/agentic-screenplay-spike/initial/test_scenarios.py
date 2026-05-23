"""TDAB scenarios as pytest tests.

Slow (~30s/scenario) and non-deterministic — keep behind the `integration` mark.
"""
import pytest

from stagentic_play import Agent, Context, then, when
from harness import SPIKE_ROOT

TASKS_DIR = SPIKE_ROOT / "fixtures/tasks"


@pytest.fixture
def context(artefacts_dir):
    return Context(
        artefacts_dir=artefacts_dir,
        cwd=SPIKE_ROOT,
        tasks_dir=TASKS_DIR,
    )


# Illustrative: agent fixtures live in the test file for now; expected
# to be configurable per-suite/per-run later.
@pytest.fixture
def agent_under_test(context):
    return Agent(model="claude-opus-4-7", context=context)


@pytest.fixture
def evaluator(context):
    return Agent(model="claude-sonnet-4-6", context=context)


@pytest.mark.integration
def test_skips_weighing_when_only_one_option_given(agent_under_test, evaluator):
    when(agent_under_test).attempts_to(
        "run-decisions-demo-with-one-option"
    )

    then(evaluator).should_see_that(agent_under_test).achieved(
        "skip-weighing-and-tell-the-user-the-choice-has-been-made"
    )
