"""Agentic aspects of screenplay: the Agent role wrapper, the AgentBackend
contract, the Transcript artefact, concrete backends (ClaudeCliAgent), the
Auditor role for code-based info retrieval, and the agentic verification
chain (then(subject).should(expectation(..., seen_by=inspector)))."""
from .agent import Agent, AgentBackend, Transcript
from .auditor import Auditor
from .claude_cli import ClaudeCliAgent
from .verification import then

__all__ = [
    "Agent",
    "AgentBackend",
    "Auditor",
    "ClaudeCliAgent",
    "Transcript",
    "then",
]
