"""Auto-discover .ability files and generate one Test class per Ability.

Each Ability becomes a Test<AbilityName> class containing one test_<scenario>
staticmethod per Scenario. Pytest-bdd's scenario wrapper has signature
(request, _pytest_bdd_example) with no `self`, so each scenario is wrapped in
@staticmethod to keep it pytest-compatible inside a class. The IDE then shows
each Ability as its own group, mirroring Test class grouping."""
from pathlib import Path

from pytest_bdd import scenario
from pytest_bdd.feature import get_features

BEHAVIOURS_DIR = Path(__file__).parent / "behaviours"


def _pascal(s):
    return "".join(w.capitalize() for w in s.replace("_", " ").replace("-", " ").split())


def _snake(s):
    return s.lower().replace(" ", "_").replace("-", "_")


_ability_paths = [str(p) for p in BEHAVIOURS_DIR.glob("**/*.ability")]
for _feature in get_features(_ability_paths):
    _cls_name = "Ability" + _pascal(_feature.name or "Anonymous")
    _attrs = {}
    for _sname in _feature.scenarios:
        _test_fn = scenario(_feature.filename, _sname)(lambda: None)
        _attrs["should_" + _snake(_sname)] = staticmethod(_test_fn)
    globals()[_cls_name] = type(_cls_name, (), _attrs)
