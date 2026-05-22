"""Expectation: the subject's transcript contains each given regex pattern
(case-insensitive), scoped by speaker.

`as_follows` is a list of (speaker, regex) pairs. Speaker is 'Agent' or
'User'. 'User' rows are translated to match the agent's transcript
convention (the agent prefixes echoed user input with 'User response:').

Dispatches to a role-specific variant based on the inspector's role:
  - Auditor: code-based regex check on the transcript text.
  - Agent:   LLM scorecard run by the critic, given the transcript path
             and pattern list via the prompt prefix."""
import re
from functools import singledispatch

from screenplay_core import Actor
from stagentic_play import Agent, Auditor


def complete_its_workflow(*, as_follows: list[tuple[str, str]], witnessed_by: Actor):
    patterns = [_translate(speaker, regex) for speaker, regex in as_follows]

    def expecting(subject: Actor) -> None:
        _check(witnessed_by.role, subject, patterns)
    return expecting


def _translate(speaker: str, regex: str) -> str:
    speaker, regex = speaker.strip(), regex.strip()
    if speaker == "User":
        return f"User response: {regex}"
    return regex


@singledispatch
def _check(role, subject: Actor, outputs_matching: list[str]) -> None:
    raise NotImplementedError(
        f"No 'complete_its_workflow' variant for role type {type(role).__name__}"
    )


@_check.register
def _(inspector: Auditor, subject: Actor, outputs_matching: list[str]) -> None:
    text = inspector.get_transcript_of(subject).text
    missing = [p for p in outputs_matching if not re.search(p, text, re.IGNORECASE)]
    assert not missing, (
        "Transcript missing patterns:\n"
        + "\n".join(f"  - /{p}/i" for p in missing)
        + f"\n\n--- transcript ---\n{text}"
    )


@_check.register
def _(inspector: Agent, subject: Actor, outputs_matching: list[str]) -> None:
    transcript_path = subject.in_character(Agent).transcript.path
    pattern_lines = "\n".join(f"- /{p}/i" for p in outputs_matching)
    prefix = (
        f"Transcript to evaluate: {transcript_path}\n\n"
        f"Patterns to verify (case-insensitive Python regex):\n"
        f"{pattern_lines}\n\n"
    )
    result = inspector.run_prompt("verify-transcript-contains-patterns", prefix=prefix)
    assert "OVERALL: PASS" in result, f"\n--- inspector output ---\n{result}"
