import pytest

from screenplay_core import Actor
from stagentic_play import Agent, Auditor, ClaudeCliAgent

from .paths import SPIKE_ROOT, TASKS_DIR


# ---- Inspector configuration markers -------------------------------------
# Empty classes used as dispatch keys in config tuples. Type tokens — IDE
# navigation and type-checker validation work; no string typos.

class ClaudeCliCritic:
    """Inspector config: a critic Actor whose Agent role is driven by the
    Claude CLI (Sonnet), judging the subject via an LLM scorecard."""


class RuntimeAuditor:
    """Inspector config: an auditor Actor whose Auditor role runs in Python
    at runtime — no LLM, code-only mechanical checks on the subject's
    transcript."""


# ---- Factories -----------------------------------------------------------

def _make_claude_cli_critic(artefacts_dir):
    return Actor("critic").playing_the(
        Agent(ClaudeCliAgent(
            model="claude-sonnet-4-6",
            cwd=SPIKE_ROOT,
            tasks_dir=TASKS_DIR,
            artefacts_dir=artefacts_dir,
            step=2, step_type="then",
        ))
    )


def _make_runtime_auditor(_artefacts_dir):
    return Actor("auditor").playing_the(Auditor())


_INSPECTORS = {
    ClaudeCliCritic: _make_claude_cli_critic,
    RuntimeAuditor: _make_runtime_auditor,
}


@pytest.fixture
def inspector(config, artefacts_dir):
    _, InspectorCls = config
    return _INSPECTORS[InspectorCls](artefacts_dir)
