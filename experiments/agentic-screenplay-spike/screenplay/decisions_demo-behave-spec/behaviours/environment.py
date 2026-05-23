"""behave lifecycle hooks: build decision_support_agent and inspector per scenario.

Reads the agent config from `-D agent=<id>` on the command line. Defaults to
real_claude__auditor — a deterministic-ish single config that exercises the
full pipeline without LLM-based judging.

Each `behave` invocation runs the suite under one agent config. To run all
four (the same matrix as the conventional pytest tests), launch four
processes in parallel.
"""
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCREENPLAY_ROOT = HERE.parent.parent
sys.path.insert(0, str(SCREENPLAY_ROOT))

from screenplay_core import Actor
from stagentic_play import Agent, Auditor, ClaudeCliAgent
from tests.fixtures.stubbed_agent import StubbedAgent
from tests.fixtures.decision_support_agent import STUBBED_TRANSCRIPT


SPIKE_ROOT = Path(__file__).resolve().parents[3]  # …/agentic-screenplay-spike/
TASKS_DIR = SPIKE_ROOT / "fixtures/tasks"


def _make_subject_backend(agent_id: str, artefacts_dir: Path):
    if agent_id.startswith("real_claude"):
        return ClaudeCliAgent(
            model="claude-opus-4-7",
            cwd=SPIKE_ROOT,
            tasks_dir=TASKS_DIR,
            artefacts_dir=artefacts_dir,
            step=1, step_type="when",
        )
    if agent_id.startswith("stubbed"):
        return StubbedAgent(
            transcript_text=STUBBED_TRANSCRIPT,
            artefacts_dir=artefacts_dir,
        )
    raise ValueError(f"unknown agent_id prefix: {agent_id!r}")


def _make_inspector(agent_id: str, artefacts_dir: Path) -> Actor:
    if agent_id.endswith("__critic"):
        return Actor("critic").playing_the(
            Agent(ClaudeCliAgent(
                model="claude-sonnet-4-6",
                cwd=SPIKE_ROOT,
                tasks_dir=TASKS_DIR,
                artefacts_dir=artefacts_dir,
                step=2, step_type="then",
            ))
        )
    if agent_id.endswith("__auditor"):
        return Actor("auditor").playing_the(Auditor())
    raise ValueError(f"unknown agent_id suffix: {agent_id!r}")


def before_scenario(context, scenario):
    agent_id = context.config.userdata.get("agent", "real_claude__auditor")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_name = scenario.name.lower().replace(" ", "-")
    artefacts_dir = (
        SPIKE_ROOT
        / f".artefacts/transcripts/{timestamp}-{test_name}"
    )
    artefacts_dir.mkdir(parents=True, exist_ok=True)

    context.decision_support_agent = Actor("decision_support_agent").playing_the(
        Agent(_make_subject_backend(agent_id, artefacts_dir))
    )
    context.inspector = _make_inspector(agent_id, artefacts_dir)
