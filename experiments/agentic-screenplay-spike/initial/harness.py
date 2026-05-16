"""Helpers for running a TDAB scenario through `claude -p`.

Composes `agent_utils.transcriber.TranscriptRenderer` to project the JSONL
that Claude writes at `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`
into the markdown file the Then-step scorecard expects.
"""
import subprocess
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "agent-utils/src"))
from agent_utils.transcriber import TranscriptRenderer  # noqa: E402

PROMPTBOOK_ROOT = Path("/workspace/stagentic-promptbook")


def new_session_id() -> str:
    return str(uuid.uuid4())


def run_claude_step(*, prompt_file: Path, cwd: Path, sid: str | None = None, prompt_prefix: str = "", model: str | None = None) -> subprocess.CompletedProcess:
    cmd = ["claude", "--permission-mode", "acceptEdits"]
    if model:
        cmd.extend(["--model", model])
    if sid:
        cmd.extend(["--session-id", sid])
    cmd.extend(["-p", prompt_prefix + prompt_file.read_text()])
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p exited {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def transcribe(*, sid: str, step: int, step_type: str, artefacts_dir: Path, cwd: Path) -> Path:
    jsonl_path = Path.home() / ".claude/projects" / _encoded_cwd(cwd) / f"{sid}.jsonl"
    output = artefacts_dir / f"{step}-{step_type}-{sid}.md"
    renderer = TranscriptRenderer()
    with open(jsonl_path) as f, open(output, "w") as out:
        for line in f:
            rendered = renderer.render_line(line)
            if rendered:
                out.write(rendered)
    with open(artefacts_dir / "agent-ids.txt", "a") as f:
        f.write(f"Step {step} ({step_type.capitalize()}): {sid} {jsonl_path}\n")
    return output


def _encoded_cwd(path: Path) -> str:
    return "-" + str(path.resolve()).strip("/").replace("/", "-")
