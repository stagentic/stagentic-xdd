"""StubbedAgent: a fake AgentBackend that returns canned transcript content
without invoking any CLI. Used for fast, deterministic scenarios."""
from __future__ import annotations

from pathlib import Path

from stagentic_play import Transcript


class StubbedAgent:
    """An AgentBackend that exposes pre-supplied transcript text.

    Constructor takes the text to return and the artefacts_dir to write it
    into. The Transcript(path=...) contract holds, and a critic running
    under `--permission-mode acceptEdits` can read the file because it
    lives under the workspace (unlike /tmp paths)."""

    def __init__(self, transcript_text: str, artefacts_dir: Path):
        path = artefacts_dir / "stubbed-transcript.md"
        path.write_text(transcript_text, encoding="utf-8")
        self.transcript: Transcript | None = Transcript(path=path)

    def run_prompt(self, name: str, *, inputs: dict | None = None, prefix: str = "") -> str:
        return ""  # no-op; transcript was set at construction
