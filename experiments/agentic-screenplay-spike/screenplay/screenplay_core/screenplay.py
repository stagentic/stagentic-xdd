"""Screenplay-style framework primitives. Pure Screenplay — no LLM, no
agent, no evaluator concepts. Those live in the sibling `stagentic_play`
package, which depends on this one.

  Actor       - performs Tasks; plays one or more Roles.
  Task        - Callable[[actor], _]. Performed by one actor.
  Expectation - Callable[[subject], _]. Vanilla (code-based) check.

Call sites:
  Actor('...').playing_the(some_role)
  when(actor).attempts_to(task)
  then(actor).attempts_to(task)
"""
from __future__ import annotations

from typing import Protocol, Type, TypeVar

T = TypeVar("T")


# ---- Actor ---------------------------------------------------------------

class Actor:
    def __init__(self, name: str):
        self.name = name
        self.role: object | None = None

    def playing_the(self, role: object) -> Actor:
        self.role = role
        return self

    def in_character(self, role_type: Type[T]) -> T:
        if isinstance(self.role, role_type):
            return self.role
        raise LookupError(
            f"{self.name} is not playing any role of type {role_type.__name__}"
        )

    def attempts_to(self, task: Task):
        return task(self)


# ---- Distinct callable shapes --------------------------------------------
# Protocols (rather than Callable aliases) so IDEs reliably resolve the type
# AND show parameter names in tooltips.

class Task(Protocol):
    """A unit of behaviour performed by an Actor."""
    def __call__(self, actor: Actor) -> object: ...


class Expectation(Protocol):
    """A code-based check: one actor inspects another. The first parameter
    is the actor playing the inspecting role (e.g. an Auditor); the second
    is the subject being inspected."""
    def __call__(self, inspector: Actor, subject: Actor) -> object: ...


# ---- when / then sugar ---------------------------------------------------
# Both 'when' and 'then' are narrative BDD verbs that wrap an Actor and
# expose .attempts_to(task). The agentic dual-actor verification chain
# (then(evaluator).should_see_that(subject).achieved(...)) is provided by
# stagentic_play, which shadows `then` for tests that need it.

def when(actor: Actor) -> _Phrase:
    return _Phrase(actor)


def then(actor: Actor) -> _Phrase:
    return _Phrase(actor)


class _Phrase:
    def __init__(self, actor: Actor):
        self.actor = actor

    def attempts_to(self, task: Task):
        return self.actor.attempts_to(task)
