import pytest

from auditor import Auditor


@pytest.fixture
def inspector():
    return Auditor()
