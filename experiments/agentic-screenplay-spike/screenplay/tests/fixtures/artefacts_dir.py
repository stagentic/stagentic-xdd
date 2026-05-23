from datetime import datetime

import pytest

from .paths import SPIKE_ROOT


@pytest.fixture
def artefacts_dir(request):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    test_name = request.node.name.removeprefix("test_").replace("_", "-")
    path = SPIKE_ROOT / f".artefacts/transcripts/{timestamp}-{test_name}"
    path.mkdir(parents=True, exist_ok=True)
    return path
