import pytest
from auditor import Auditor


def pytest_addoption(parser):
    parser.addoption("--inspector", default="auditor", choices=["auditor"])


@pytest.fixture
def inspector(request):
    match request.config.getoption("--inspector"):
        case "auditor":
            return Auditor()
