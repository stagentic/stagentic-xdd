from unittest.mock import MagicMock

import pytest


@pytest.fixture
def dummy():
    return MagicMock()
