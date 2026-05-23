"""Shared path constants for fixtures."""
from pathlib import Path

SPIKE_ROOT = Path(__file__).resolve().parents[3]  # …/agentic-screenplay-spike/
TASKS_DIR = SPIKE_ROOT / "fixtures/tasks"
