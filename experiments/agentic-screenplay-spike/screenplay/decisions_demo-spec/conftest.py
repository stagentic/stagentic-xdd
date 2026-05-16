"""Spec-dir conftest for decisions_demo-spec.

- Autouse fixture forces the `config` parametrize chain to fan out across
  the 4 configs (auto-generated tests have no fixture args in their
  signatures, so the chain wouldn't otherwise expand at collection).
- Imports `steps` for side-effect step-def registration; pytest-bdd does
  not auto-scan arbitrary modules."""
import pytest

from steps import *  # noqa: F401,F403 — pulls @when_step/@then_step fns into scope


@pytest.fixture(autouse=True)
def _force_config_parametrize(config):
    return config
