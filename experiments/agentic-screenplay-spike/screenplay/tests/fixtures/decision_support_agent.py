import pytest

from screenplay_core import Actor
from stagentic_play import Agent, ClaudeCliAgent

from .paths import PROMPTBOOK_ROOT, TASKS_DIR
from .stubbed_agent import StubbedAgent


STUBBED_TRANSCRIPT = """\
`17:15:50Z` [TOOL] **Skill** `stagentic-promptbook:decisions-demo`

`17:15:54Z` [TOOL] **Read** `/workspace/stagentic-promptbook/skills/decisions-demo/decisions-demo.puml`

`17:16:00Z`

**Ask**: What are you choosing between? List 2 to 5 options, one per line.

User response: pizza

**Input**: options = `pizza`

Only one option provided — taking the `yes` branch.

**Inform**: Looks like you only gave me one option. The decision is already made.
"""


def _make_claude_cli_backend(artefacts_dir):
    return ClaudeCliAgent(
        model="claude-opus-4-7",
        cwd=PROMPTBOOK_ROOT,
        tasks_dir=TASKS_DIR,
        artefacts_dir=artefacts_dir,
        step=1, step_type="when",
    )


def _make_stubbed_backend(artefacts_dir):
    return StubbedAgent(transcript_text=STUBBED_TRANSCRIPT, artefacts_dir=artefacts_dir)


_BACKENDS = {
    ClaudeCliAgent: _make_claude_cli_backend,
    StubbedAgent: _make_stubbed_backend,
}


@pytest.fixture
def decision_support_agent(config, artefacts_dir):
    BackendCls, _ = config
    backend = _BACKENDS[BackendCls](artefacts_dir)
    return Actor("decision_support_agent").playing_the(Agent(backend))
