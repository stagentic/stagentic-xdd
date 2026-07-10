from contextlib import nullcontext as does_not_raise

import pytest

from conftest import _reject_incompatible_inspector


class TestInspectorGuard:
    def test_should_reject_the_auditor_judging_the_real_agent(self):
        with pytest.raises(pytest.UsageError, match="deterministic"):
            _reject_incompatible_inspector(agent="real", inspector="auditor")

    def test_should_allow_the_auditor_to_judge_the_fake_agent(self):
        with does_not_raise():
            _reject_incompatible_inspector(agent="fake", inspector="auditor")
