# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Swap the fake agent for the real claude CLI

`--agent=real` is wired into `spec/conftest.py`. `Agent` (in `play/src/agent.py`)
calls `claude -p` via `ClaudeCli`, generates a session ID, and delegates transcript
rendering to an injected transcriber callable. `Transcriber` (in `play/src/transcriber.py`)
renders JSONL to markdown and is approved-tested against a real run fixture.

What remains before `--agent=real` can run end-to-end:

1. **Refactor `Transcriber`** — `Agent` injects a transcriber callable with the
   signature `(jsonl_path, output_path)`. `Transcriber.render(jsonl_path)` returns
   a string; there is a mismatch. Refactor `Transcriber` so it can serve directly
   as that callable (or as the source of one), test-driving the change.

2. **Wire the JSONL path into `Agent`** — `Agent.perform()` currently passes `None`
   as the JSONL path to the transcriber. The JSONL lands at
   `~/.claude/projects/<encoded-cwd>/<sid>.jsonl` where
   `encoded-cwd = "-" + cwd.strip("/").replace("/", "-")`.
   Test-drive the path computation, then pass the real path to the transcriber.

3. **Wire `Transcriber` into the `Agent` fixture** — `spec/conftest.py` currently
   injects a no-op `lambda` as the transcriber. Replace it with the real transcriber.

4. **Watch real run** — run the scenario under `--agent=real` to see what the
   agent actually does and what the transcript contains.

5. **Test-drive any harness changes** — drive fixes through unit tests
   before wiring them up.
   *(cf. `9ccdbc4`, `01c965c`, `546fe91`, `b862c2d`)*

6. **Integration tests last** — once the scenario is green under
   `--agent=real`, add integration tests for the real-agent path one
   at a time.
   *(cf. `ea7b497`)*

Once `--agent=real` is green, commit `spec/conftest.py`, `COMMANDS.md`,
and `spec/tasks/1-first-test-for-miles-to-km-converter/TASK.md` together.

## Future want: preserve test artefacts

Add an `--artefacts-dir <path>` CLI option to `spec/conftest.py`. When
provided, the full tmp workspace (code, transcript, etc.) is copied into a
datestamped subdirectory of the given path after each scenario run. The
subdirectory name should follow the convention used in
`experiments/agentic-screenplay-spike/.artefacts/` (e.g.
`20260527-143012-<scenario-slug>/`).

**Naming convention** when artefacts are preserved:
- Folder: `<timestamp>-<test_function_name>/` (e.g. `20260527-060502-test_write_a_failing_test/`)
- File: `<task-name>-<sid-prefix-8>.md` (e.g. `1-first-test-for-miles-to-km-converter-cabd5050.md`)
- Critic transcript (future): same folder, distinguished by suffix (e.g. `-critic-<sid>.md`)

For now, `transcript.md` in `tmp_path` is sufficient. The naming convention and folder structure land with `--artefacts-dir`.

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
