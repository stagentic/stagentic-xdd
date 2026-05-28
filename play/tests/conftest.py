import pytest
from unittest.mock import MagicMock


@pytest.fixture
def dummy():
    return MagicMock()

