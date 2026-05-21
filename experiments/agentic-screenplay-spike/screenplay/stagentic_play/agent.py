"""Agent role and the seam for plugging in a concrete LLM backend.

  Agent        - the role an Actor plays when acting as an LLM agent.
                 Wraps a concrete AgentBackend.
  AgentBackend - Protocol any concrete backend must satisfy.
  Transcript   - readable artefact a backend produces after running prompts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class Transcript:
    """A readable artefact a backend produced after running prompts.

    Each backend constructs one after each run_prompt; the Agent wrapper
    exposes it. Minimal v1 contract:
      .path : where the readable file lives
      .text : its contents, lazy-read

    Backends MAY subclass for richer access later (e.g. structured turns,
    tool-call extraction). LLM expectations inject .path into the prompt
    prefix; code expectations search .text."""
    path: Path

    @property
    def text(self) -> str:
        return self.path.read_text()


@runtime_checkable
class AgentBackend(Protocol):
    """A concrete backend an Agent can use to drive an LLM.

    Concrete backends (ClaudeCliAgent, OpenAiCliAgent, MyCustomAgent) own:
      - how to invoke their LLM (subprocess, API, custom harness)
      - where their native log lives and its format
      - how to render that log into a Transcript an evaluator can read
    """
    transcript: Transcript | None
    def run_prompt(self, name: str, *, inputs: dict | None = None, prefix: str = "") -> str: ...


class Agent:
    """The role an actor plays: acting as an LLM agent.

    Wraps a concrete AgentBackend. Tasks always interact with Agent;
    swapping the backend is a fixture change, not a Task change."""

    def __init__(self, backend: AgentBackend):
        self._backend = backend

    @property
    def transcript(self) -> Transcript | None:
        return self._backend.transcript

    def run_prompt(self, name: str, *, inputs: dict | None = None, prefix: str = "") -> str:
        return self._backend.run_prompt(name, inputs=inputs, prefix=prefix)
