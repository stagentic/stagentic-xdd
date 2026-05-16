"""Shared path constants for fixtures."""
from pathlib import Path


def _workspace_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "stagentic-promptbook").is_dir():
            return parent
    raise RuntimeError("Could not locate stagentic-promptbook sibling")


PROMPTBOOK_ROOT = _workspace_root() / "stagentic-promptbook"
TASKS_DIR = PROMPTBOOK_ROOT / "promptbook-spec/behaviours/decisions-demo/tasks"
