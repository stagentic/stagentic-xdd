"""Agentic verification chain: a subject Actor's behaviour is verified by
an inspector Actor (Auditor for code-based, Agent for LLM-based). The
inspector is captured by the expectation factory via `witnessed_by=`; the
call chain reads:

  then(subject).should(expectation_factory(..., witnessed_by=inspector))
"""
from __future__ import annotations

from typing import Callable

from screenplay_core import Actor, Task


def then(subject: Actor) -> _Then:
    return _Then(subject)


class _Then:
    def __init__(self, subject: Actor):
        self.subject = subject

    def attempts_to(self, task: Task):
        return self.subject.attempts_to(task)

    def should(self, expectation: Callable[[Actor], None]) -> None:
        expectation(self.subject)
