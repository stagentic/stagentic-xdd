"""Expectation: the decision_support_agent gave the right answer by skipping weighing.

Dispatches to a role-specific variant based on the inspector's role:
  - Auditor: code-based check on the transcript text.
  - Agent:   LLM-based scorecard run by the critic.

Test bodies use the same expectation name; the fixture (critic / auditor)
determines which variant runs."""
import re
from functools import singledispatch

from screenplay_core import Actor
from stagentic_play import Agent, Auditor


_ASKS_FRAMING_QUESTION = re.compile(r"What are you choosing between\?")
_ACKNOWLEDGES_ONE_OPTION = re.compile(r"Looks like you only gave me one option")
_DECISION_MADE = re.compile(
    r"the (?:choice|decision) (?:is|has been) (?:already )?made",
    re.IGNORECASE,
)


def the_right_answer_by_skipping_weighing(*, seen_by: Actor):
    def expecting(subject: Actor) -> None:
        _check(seen_by.role, subject)
    return expecting


@singledispatch
def _check(role, subject: Actor) -> None:
    raise NotImplementedError(
        f"No 'the_right_answer_by_skipping_weighing' variant for role type "
        f"{type(role).__name__}"
    )


@_check.register
def _(inspector: Auditor, subject: Actor) -> None:
    text = inspector.get_transcript_of(subject).text
    assert _ASKS_FRAMING_QUESTION.search(text), \
        f"agent did not ask the framing question.\n\n{text}"
    assert _ACKNOWLEDGES_ONE_OPTION.search(text), \
        f"agent did not acknowledge that only one option was given.\n\n{text}"
    assert _DECISION_MADE.search(text), \
        f"agent did not state the decision is/has been made.\n\n{text}"


@_check.register
def _(inspector: Agent, subject: Actor) -> None:
    result = inspector.run_prompt(
        "skip-weighing-and-tell-the-user-the-choice-has-been-made",
        prefix=(
            f"The transcript to evaluate is at:\n"
            f"{subject.in_character(Agent).transcript.path}\n\n"
            "Read that file directly; skip the folder-matching and "
            "agent-ids.txt steps in the task below.\n\n"
        ),
    )
    assert "OVERALL: PASS" in result, f"\n--- evaluator output ---\n{result}"
