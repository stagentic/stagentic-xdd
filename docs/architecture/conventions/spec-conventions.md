# Spec conventions

Naming and design-intent conventions for `spec/` that should persist across refactors. A fresh contributor might be tempted to "improve" these names; this document captures why each one is the way it is.

## The `working_dir` parameter

The path bound to `working_dir` in `spec/tests/test_*.py` appears in four places: as a `copytree` destination during setup, as the `working_dir=` kwarg to `agent.perform`, as the `working_dir=` kwarg to `inspector.evaluate`, and as the second positional argument to `_have(...)` where the verify callables read it. All four keep the name `working_dir`, including the parameter inside `_have`.

**Why:** the auditor is not inspecting a separate "result" artefact. It is inspecting the working directory and asking "does this directory now reflect the expected end-state?" The working dir is the unified subject across all phases of the test; calling it `result` inside `_have` would imply a distinct produced artefact that does not exist. The lifecycle of one directory is what the test is about.

**Trigger to revisit:** if the auditor's contract genuinely changes — e.g. it begins evaluating something other than the working dir's state (a returned value, a side-channel) — that is the moment to revisit. Otherwise the name stays.

## The `transcript` parameter

The first parameter of `verify` callables in scorecard rows is named `transcript`. The auditor passes the transcript file's text content; the callable interrogates it (e.g. regex-matching recorded tool calls).

**Why:** the parameter names what the value *is* — the transcript of the agent's session — rather than the role it plays inside the lambda (`text`, `content`, `data`). A reader of a scorecard row sees what is being interrogated without scanning the harness wiring.

## Scene projects explained

Each `tasks/N-name/scene/` is a runnable Python project — `uv sync && uv run pytest tests/` at the scene root works.

- `pyproject.toml` at scene root with `[tool.pytest.ini_options] pythonpath = ["src"]` and `[tool.uv] package = false`.
- `uv.lock` committed for deterministic `uv sync`.
- Production code lives in `src/`, tests in `tests/`; tests import directly (e.g. `from conversion import miles_to_km`, no `src.` prefix).

`0-placeholder/scene/` carries the same `pyproject.toml` and `uv.lock` (byte-identical copies) so the agent's `uv run` in the inherited workspace lands in the scene's own project rather than walking up to `spec/pyproject.toml`.

**Why:** project setup is shared infrastructure, not something each task produces.
