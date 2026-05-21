"""Pytest DSL for TDAB scenarios run via `claude -p`.

Illustrative shape — exploring how a TDAB scenario can read in pytest.
Naming and structure are exploratory and expected to evolve.

The DSL (two-agent shape):

    when(agent_under_test).attempts_to(task_name)
    then(evaluator).should_see_that(agent_under_test).achieved(scorecard_name)

Each `Agent` is constructed with the `Context` it operates in *and* with its
own session id. The session id is decided at construction time, so the agent
carries its identity from the moment it exists — passing `agent_under_test`
to the Then step is how the evaluator finds the transcript to score.
"""
from dataclasses import dataclass, field
from pathlib import Path

from harness import new_session_id, run_claude_step, transcribe


@dataclass
class Context:
    artefacts_dir: Path
    cwd: Path
    tasks_dir: Path


@dataclass
class Agent:
    model: str
    context: Context
    sid: str = field(default_factory=new_session_id)
    transcript: Path | None = None  # set after the agent's step runs


def when(agent):
    return When(agent)


class When:
    def __init__(self, agent):
        self.agent = agent

    def attempts_to(self, task):
        ctx = self.agent.context
        run_claude_step(
            prompt_file=ctx.tasks_dir / f"{task}.md",
            sid=self.agent.sid, cwd=ctx.cwd, model=self.agent.model,
        )
        self.agent.transcript = transcribe(
            sid=self.agent.sid, step=1, step_type="when",
            artefacts_dir=ctx.artefacts_dir, cwd=ctx.cwd,
        )


def then(evaluator):
    return Then(evaluator)


class Then:
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.agent_under_test = None

    def should_see_that(self, agent_under_test):
        self.agent_under_test = agent_under_test
        return self

    def achieved(self, scorecard):
        ctx = self.evaluator.context
        result = run_claude_step(
            prompt_file=ctx.tasks_dir / f"{scorecard}.md",
            sid=self.evaluator.sid, cwd=ctx.cwd, model=self.evaluator.model,
            prompt_prefix=(
                f"The transcript to evaluate is at:\n{self.agent_under_test.transcript}\n\n"
                "Read that file directly; skip the folder-matching and "
                "agent-ids.txt steps in the task below.\n\n"
            ),
        )
        self.evaluator.transcript = transcribe(
            sid=self.evaluator.sid, step=2, step_type="then",
            artefacts_dir=ctx.artefacts_dir, cwd=ctx.cwd,
        )
        assert "OVERALL: PASS" in result.stdout
