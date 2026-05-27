# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Swap the fake agent for the real claude CLI

`FakeAgent` is wired into the spec via an `agent` fixture in
`spec/conftest.py`. `FakeAgent(tasks=…).perform(task=name, working_dir=…)`
looks up `<tasks>/<name>/fake-task.sh` and runs it; the resulting
`transcript.md` path is held on `agent.transcript`. The variation between
fake and real is only the command that interprets the task — fake runs a
shell script, real will run `claude -p` with a prompt referencing the task.

1. **Make the agent injectable** — add a `--agent` CLI option in
   `spec/conftest.py` (paralleling `--inspector=auditor|critic`).
   Only `fake` is wired; `real` is not yet a valid choice.
   *(cf. `0849177`, `45da208`, `1c1213e`)*

2. **Watch real fail** — add the real-claude implementation behind
   `--agent=real` and run the scenario to see what the agent actually
   does and what the transcript contains.

3. **Test-drive any harness changes** — drive fixes through unit tests
   before wiring them up.
   *(cf. `9ccdbc4`, `01c965c`, `546fe91`, `b862c2d`)*

4. **Integration tests last** — once the scenario is green under
   `--agent=real`, add integration tests for the real-agent path one
   at a time.
   *(cf. `ea7b497`)*

## Future want: preserve test artefacts

Add an `--artefacts-dir <path>` CLI option to `spec/conftest.py`. When
provided, the full tmp workspace (code, transcript, etc.) is copied into a
datestamped subdirectory of the given path after each scenario run. The
subdirectory name should follow the convention used in
`experiments/agentic-screenplay-spike/.artefacts/` (e.g.
`20260527-143012-<scenario-slug>/`).

Two implementation options:

**Option A: `archiver` fixture**
- An `archiver` fixture is injected into each scenario test. No-op by default;
  when `--artefacts-dir` is set, the real archiver copies the workspace in its
  finalizer (which runs after the test, while `tmp_path` is still intact).
- Consistent with the existing `--agent` / `--inspector` injectable pattern.
- Each test must explicitly request the fixture — as the number of test files
  grows, this must be repeated in every scenario or moved to `conftest.py` as
  an `autouse` fixture.

**Option B: `pytest_runtest_makereport` hook**
- A hook in `conftest.py` fires after every test automatically. If
  `--artefacts-dir` is set, it copies `tmp_path` to the artefacts dir.
- No per-test fixture request needed — scales automatically as new test files
  are added.
- Less consistent with the existing injectable pattern; hook logic is harder
  to unit-test than a fixture class.

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
