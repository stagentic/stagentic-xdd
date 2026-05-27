# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Refactoring pass

Review all production code in `play/src/` and `spec/` and leave it in good
shape before the xdd skill work begins.

## Write the xdd skill

The harness is fully wired: `--agent=real` runs the real `claude -p`, renders
the JSONL transcript, and evaluates the scorecard. A real run confirms all five
scorecard checks fail — the agent lacks the guidance a skill would provide.

The workspace already has `spec/tasks/0-placeholder/scene/.claude/settings.json`
allowing `Bash(uv run pytest*)`, so the agent can run tests once the skill
steers it correctly.

The skill needs to guide the agent to:
1. Replace the placeholder test with a failing test that imports from `conversion`.
2. Create a stub `src/conversion.py` so the test fails at assertion (not import).
3. Run `uv run pytest` and confirm the result is `FAILED`.

Once `--agent=real` is green:
- Add integration tests for the real-agent path one at a time.
  *(cf. `ea7b497`)*
- Commit `spec/conftest.py`, `COMMANDS.md`, `TASK.md`, and
  `0-placeholder/scene/.claude/settings.json` together.

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
