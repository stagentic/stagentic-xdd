"""ClaudeCliAgent: an AgentBackend that drives the Claude CLI as a subprocess.

Owns:
  - one session id (decided at construction)
  - subprocess invocation of `claude -p`
  - projection of the JSONL Claude writes into a markdown Transcript
"""
from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

from .agent import Transcript

REPO_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO_ROOT / "agent-utils/src"))
from agent_utils.transcriber import TranscriptRenderer  # noqa: E402


class ClaudeCliAgent:
    """Drive an LLM by invoking the Claude CLI as a subprocess."""

    def __init__(
        self,
        *,
        model: str,
        cwd: Path,
        tasks_dir: Path,
        artefacts_dir: Path,
        step: int,
        step_type: str,
    ):
        self.model = model
        self.cwd = cwd
        self.tasks_dir = tasks_dir
        self.artefacts_dir = artefacts_dir
        self.step = step
        self.step_type = step_type
        self.sid = str(uuid.uuid4())
        self.transcript: Transcript | None = None  # populated after each run_prompt

    def run_prompt(self, name: str, *, inputs: dict | None = None, prefix: str = "") -> str:
        prompt_path = self.tasks_dir / f"{name}.md"
        prepend = (self._render_inputs(inputs) if inputs else "") + prefix
        cmd = [
            "claude", "--permission-mode", "acceptEdits",
            "--model", self.model,
            "--session-id", self.sid,
            "-p", prepend + prompt_path.read_text(),
        ]
        result = subprocess.run(
            cmd, cwd=str(self.cwd), capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude -p exited {result.returncode}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        self.transcript = Transcript(path=self._project_jsonl_to_markdown())
        return result.stdout

    def _project_jsonl_to_markdown(self) -> Path:
        jsonl_path = (
            Path.home() / ".claude/projects" / self._encoded_cwd / f"{self.sid}.jsonl"
        )
        output = self.artefacts_dir / f"{self.step}-{self.step_type}-{self.sid}.md"
        renderer = TranscriptRenderer()
        with open(jsonl_path) as src, open(output, "w") as dst:
            for line in src:
                rendered = renderer.render_line(line)
                if rendered:
                    dst.write(rendered)
        with open(self.artefacts_dir / "agent-ids.txt", "a") as f:
            f.write(
                f"Step {self.step} ({self.step_type.capitalize()}): "
                f"{self.sid} {jsonl_path}\n"
            )
        return output

    @property
    def _encoded_cwd(self) -> str:
        return "-" + str(self.cwd.resolve()).strip("/").replace("/", "-")

    def _render_inputs(self, inputs: dict) -> str:
        # Placeholder for future Cucumber-style data-table inputs.
        # Not exercised by the current scenario.
        lines = ["Inputs:"]
        for k, v in inputs.items():
            lines.append(f"- {k}: {v}")
        return "\n".join(lines) + "\n\n"
