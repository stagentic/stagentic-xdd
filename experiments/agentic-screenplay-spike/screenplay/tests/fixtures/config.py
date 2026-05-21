"""Parametrized config fixture: each test runs against every (backend, inspector)
combination.

Config tuples reference real class types — `(ClaudeCliAgent, ClaudeCliCritic)`
etc. — so the IDE can navigate to definitions and the type checker can
validate. The decision_support_agent and inspector fixtures dispatch on these
class keys via dicts in their respective fixture modules."""
import pytest

from stagentic_play import ClaudeCliAgent

from .inspector import ClaudeCliCritic, RuntimeAuditor
from .stubbed_agent import StubbedAgent


@pytest.fixture(params=[
    pytest.param((ClaudeCliAgent, ClaudeCliCritic), id="real_claude__critic"),
    pytest.param((ClaudeCliAgent, RuntimeAuditor),  id="real_claude__auditor"),
    pytest.param((StubbedAgent,   ClaudeCliCritic), id="stubbed__critic"),
    pytest.param((StubbedAgent,   RuntimeAuditor),  id="stubbed__auditor"),
])
def config(request):
    """Tuple of (backend_class, inspector_class). Read by decision_support_agent
    and inspector fixtures to dispatch to the right factory."""
    return request.param
