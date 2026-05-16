"""Screenplay-style framework primitives.

Pure Screenplay — Actor, Task, Expectation, basic when/then sugar.
The agentic layer (Agent, AgentBackend, Transcript, agentic verification
chain, ClaudeCliAgent) lives in the sibling `stagentic_play` package."""
from .screenplay import Actor, Expectation, Task, then, when

__all__ = [
    "Actor",
    "Expectation",
    "Task",
    "then",
    "when",
]
