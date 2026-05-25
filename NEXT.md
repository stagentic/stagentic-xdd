# NEXT

## Runnable-scene pattern for new scenes

Scene 1 (`tasks/1-first-test-for-miles-to-km-converter/scene/`) is a
runnable Python project: `uv run pytest tests/` at the scene root
exits 1 with an assertion-shaped failure. The pattern, to be inherited
by every new scene added to the chain:

- `pyproject.toml` at scene root with `[tool.pytest.ini_options]
  pythonpath = ["src"]` and `[tool.uv] package = false`.
- `uv.lock` committed for deterministic `uv sync`.
- `src/` and `tests/` carry real content (no empty stub files).
- `transcript.md` carries plausible pytest output.

Scene 0 (`0-placeholder`) follows the pattern as far as the agent
needs to operate in it: `pyproject.toml` + `uv.lock` (byte-identical
copies of scene 1's, since project setup is shared infrastructure
rather than something each task produces). No `src/` or
`transcript.md` — no agent work has happened yet at the start of
task 1.

## Live constraint once the agent is real

`_fake_agent_performs` does `copytree(scene, workspace,
dirs_exist_ok=True)`. The fake agent generates no transient files,
but a real `claude -p` running `uv run pytest` inside the workspace
will produce `.venv/`, `.pytest_cache/`, and `__pycache__/`. The
auditor characteristic "Workspace state matches the expected
end-state" then sees those as unexpected.

When swapping to the real agent (per ADR 0001), either give
`_tree_diff` an ignore list or require the agent to clean transient
artefacts before reporting done.

Related: the agent's working directory must be the workspace root
(where the scene's `pyproject.toml` lives). Invoking `uv` from a
parent dir walks up to `spec/pyproject.toml` and runs against the
wrong project.

## Suggested next step

Pick between:

- (a) drive task 2 (the green step) in via TDAB:
    1. Write the scenario for the green step in `spec/tests/` —
       new test method plus scorecard of characteristics describing
       what "agent made the failing test pass" looks like.
    2. Run it red — it fails because `tasks/2-…/scene/` doesn't
       exist (the test crashes trying to copy from a missing dir).
    3. Add `tasks/2-…/scene/` following the runnable-scene pattern
       so the scenario goes green (tautologically with the fake
       agent; meaningfully once `claude -p` is swapped in).
- (b) swap `_fake_agent_performs` for `claude -p` against task 1.
  The scorecard characteristics already exist in
  `test_red_green_into_refactor.py`; the swap is what makes them
  live rather than tautological.
