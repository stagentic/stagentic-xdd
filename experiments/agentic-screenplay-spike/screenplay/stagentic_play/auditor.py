"""Auditor role: a non-LLM Actor that fetches information from a subject.

Symmetric with the Agent role — both are things an Actor plays. The Auditor's
job is to pull info from a subject (the test's 'star' actor) for code-based
expectations to inspect mechanically."""
from __future__ import annotations

from screenplay_core import Actor

from .agent import Agent, Transcript


class Auditor:
    """A role for reading information from a subject Actor.

    v1 ships one method: get_transcript_of. Future variants or subclasses
    could extract structured turns, tool-call lists, or other shapes."""

    def get_transcript_of(self, subject: Actor) -> Transcript:
        transcript = subject.in_character(Agent).transcript
        if transcript is None:
            raise RuntimeError(
                f"{subject.name}'s Agent has no transcript yet — "
                "did the When step run?"
            )
        return transcript
