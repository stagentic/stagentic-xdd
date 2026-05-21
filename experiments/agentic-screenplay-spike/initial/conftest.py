from datetime import datetime

import pytest

from harness import PROMPTBOOK_ROOT


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: end-to-end test that invokes real `claude -p`"
    )


@pytest.fixture
def artefacts_dir(request):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_name = request.node.name.removeprefix("test_").replace("_", "-")
    path = PROMPTBOOK_ROOT / f"promptbook-spec-artefacts/transcripts/{timestamp}-{test_name}"
    path.mkdir(parents=True, exist_ok=True)
    return path
