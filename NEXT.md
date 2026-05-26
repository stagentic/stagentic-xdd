# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Swap the fake agent for the real claude CLI

`_fake_agent_performs` in `spec/tests/test_red_green_commit.py` copies
a canned `scene/` over the workspace and returns a pre-written
transcript. The next step is replacing it with a real `claude -p`
invocation.

Follow the same pattern used for the critic:

1. **Wire the option, disable until green** — add a `--agent` CLI
   option to `spec/conftest.py` (default: `fake`; option: `real`).
   Keep `fake` working and commit. Do not commit `real` until the
   scenario passes under it.
   *(cf. `0849177`, `45da208`, `1c1213e`)*

2. **Watch it fail** — run the scenario under `--agent=real` to see
   what the agent actually does and what the transcript contains.

3. **Test-drive any harness changes** — drive fixes through unit tests
   before wiring them up.
   *(cf. `9ccdbc4`, `01c965c`, `546fe91`, `b862c2d`)*

4. **Integration tests last** — once the scenario is green under
   `--agent=real`, add integration tests for the real-agent path one
   at a time.
   *(cf. `ea7b497`)*

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
