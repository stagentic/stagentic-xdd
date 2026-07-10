import pytest

from conftest import _reject_incompatible_inspector


class TestInspectorGuard:
    def test_should_reject_the_auditor_judging_the_real_agent(self):
        with pytest.raises(pytest.UsageError, match="deterministic"):
            _reject_incompatible_inspector(agent="real", inspector="auditor")
