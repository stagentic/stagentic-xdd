from pathlib import Path

import pytest
from archiver import archive, current_timestamp
from auditor import Auditor
from critic import Critic
from claude_cli import ClaudeCli
from fake_agent import FakeAgent

TASKS = Path(__file__).parent / "tasks"


def pytest_addoption(parser):
    parser.addoption("--inspector", default="auditor", choices=["auditor", "critic"])
    parser.addoption("--.artefacts-dir", default=None)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    archive(
        phase=call.when,
        tmp_path=item.funcargs.get("tmp_path"),
        test_name=item.name,
        artefacts_dir=item.config.getoption("--.artefacts-dir"),
        timestamp=current_timestamp(),
    )


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
