# NEXT

## Make each `scene/` a runnable Python project

Scene content today is just enough to satisfy the auditor's regex/size
checks. The next move is to make each `scene/` a runnable Python
project — so a real agent can `uv run pytest tests/` in the workspace
it inherits.

Known constraints from earlier exploration:

- **`_fake_agent_performs` does `copytree(scene, workspace)`.**
  Anything in `scene/` ends up in the workspace. Transient artefacts
  (`.venv/`, `.pytest_cache/`, `__pycache__/`) created by running `uv`
  inside a scene for verification will pollute the workspace and break
  tree-diff. Either keep `scene/` strictly clean, or give `copytree`
  (and possibly `_tree_diff`) an ignore list.

- **Imports need a sys.path entry.** Pytest's default import mode adds
  `tests/` (the test file's first ancestor without `__init__.py`) to
  `sys.path`, not the scene root. Earlier exploration: `pyproject.toml`
  at the scene root with `[tool.pytest.ini_options] pythonpath = ["src"]`
  works, and tests import as `from conversion import miles_to_km` (no
  `src.` prefix).

- **`uv.lock` open question.** Committing it gives tree-diff stability
  (the workspace inherits it deterministically). Skipping it means the
  real agent's first `uv sync` generates a lockfile that tree-diff sees
  as unexpected. Lean: commit it.

Suggested first step: propose the structure for one scene
(`tasks/1-first-test-for-miles-to-km-converter/scene/`) and verify it
runs via `uv run --directory <scene> pytest tests/` before applying
across the chain. Once a scene contains `pyproject.toml`, every
subsequent scene must too, and the tree-diff baseline shifts.
