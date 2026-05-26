import pytest


def pytest_addoption(parser):
    parser.addoption("--claude", default="stub", choices=["stub"])


@pytest.fixture
def claude_cli(request):
    match request.config.getoption("--claude"):
        case "stub":
            return None
