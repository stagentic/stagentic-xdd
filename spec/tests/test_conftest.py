from contextlib import nullcontext as does_not_raise

import pytest
from cases import case

from conftest import _reject_incompatible_inspector


class TestInspectorGuard:
    @pytest.mark.parametrize("agent, inspector, expectation", [
        case(
            "the-real-agent-defaults-to-the-critic",
            agent="real", inspector=None, expectation=does_not_raise(),
        ),
        case(
            "the-auditor-judging-the-real-agent-is-rejected",
            agent="real", inspector="auditor",
            expectation=pytest.raises(pytest.UsageError, match="deterministic"),
        ),
        case(
            "the-auditor-may-judge-the-fake-agent",
            agent="fake", inspector="auditor", expectation=does_not_raise(),
        ),
        case(
            "the-critic-may-judge-the-real-agent",
            agent="real", inspector="critic", expectation=does_not_raise(),
        ),
    ])
    def test_should_reject_only_the_auditor_judging_the_real_agent(
        self, agent, inspector, expectation
    ):
        with expectation:
            _reject_incompatible_inspector(agent=agent, inspector=inspector)
