"""Pytest root conftest. Imports fixtures from tests/fixtures/ so pytest
discovers them, registers markers, and deselects parametrized variants
whose config id doesn't match a test's @configs marker (if present)."""

import pytest

from tests.fixtures.decision_support_agent import decision_support_agent  # noqa: F401
from tests.fixtures.artefacts_dir import artefacts_dir  # noqa: F401
from tests.fixtures.config import config  # noqa: F401
from tests.fixtures.inspector import inspector  # noqa: F401


_pytest_config = None
_last_cfg_seen = None


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: end-to-end test that invokes real `claude -p`"
    )
    config.addinivalue_line(
        "markers",
        "configs(*ids): restrict the parametrized configs this test runs in. "
        "Each arg is a substring matched against the parametrize id; the test "
        "runs only for configs whose id matches at least one arg.",
    )
    global _pytest_config
    _pytest_config = config


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logstart(nodeid, location):
    """Print a separator banner the first time each config is seen, so the
    matrix output groups visibly by config (outer loop). `tryfirst` makes
    our hook run before pytest's default terminalreporter logstart, so the
    banner lands above the first nodeid line of each group."""
    global _last_cfg_seen
    lb, rb = nodeid.rfind("["), nodeid.rfind("]")
    if lb == -1 or rb == -1:
        return
    cfg = nodeid[lb + 1:rb]
    if cfg == _last_cfg_seen:
        return
    _last_cfg_seen = cfg
    tr = _pytest_config.pluginmanager.getplugin("terminalreporter") if _pytest_config else None
    if tr is not None:
        tr.write_line("")
        tr.write_sep("=", f"Config: {cfg}", bold=True)


def pytest_collection_modifyitems(config, items):
    """1) Deselect parametrized variants whose config id doesn't match the
    test's @pytest.mark.configs(...) marker (if any).
    2) Re-order so config is the outer loop, ability file the middle loop,
    scenario the inner loop. Non-bdd items fall back to (cfg, .py path, name)."""
    remaining, deselected = [], []
    for item in items:
        marker = item.get_closest_marker("configs")
        cfg_id = getattr(getattr(item, "callspec", None), "id", None)
        if marker is None or cfg_id is None or any(
            token in cfg_id for token in marker.args
        ):
            remaining.append(item)
        else:
            deselected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)

    def _sort_key(item):
        cfg_id = getattr(getattr(item, "callspec", None), "id", "") or ""
        scenario = getattr(item.function, "__scenario__", None)
        if scenario is not None:
            return (cfg_id, scenario.feature.filename, scenario.name)
        return (cfg_id, str(item.path), item.originalname or item.name)

    remaining.sort(key=_sort_key)
    items[:] = remaining
