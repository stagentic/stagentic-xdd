from pathlib import Path

import pytest
from auditor import Auditor
from critic import Critic
from claude_cli import ClaudeCli
from fake_agent import FakeAgent

TASKS = Path(__file__).parent / "tasks"


def pytest_addoption(parser):
    parser.addoption("--inspector", default="auditor", choices=["auditor", "critic"])


@pytest.fixture
def inspector(request):
    match request.config.getoption("--inspector"):
        case "auditor":
            return Auditor()
        case "critic":
            return Critic(claude=ClaudeCli())


@pytest.fixture
def agent():
    return FakeAgent(tasks=TASKS)
