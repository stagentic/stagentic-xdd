# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Working approach

1. Propose a test — await explicit approval before writing it.
2. Write the test and run it.
3. Understand the failure — propose the minimum change to address only that failure.
4. Await approval — answering a clarifying question is not approval.
5. Apply the change and repeat from 2 until green.
6. On green: run all baseline configs below — all must pass before proposing a commit:
   - `uv run --directory play pytest` — full play unit/integration/contract suite
   - `uv run --directory spec pytest tests` — fake agent, auditor (default)
   - `uv run --directory spec pytest tests --inspector=critic` — fake agent, real critic
   - Real agent excluded while the xdd skill is in development.
7. Commits are proposed only — never applied until the user gives express approval.
8. Repeat from 1 until the work item is complete.

## 1. Preserve critic transcript as `critique.md`

When `--.artefacts-dir` is set and `--inspector=critic`, the critic's output
should be saved alongside `transcript.md` as `critique.md` in the same
artefacts folder. Same rendered markdown format as `transcript.md`.

### How the existing artefacts mechanism works

`spec/archiver.py` has two public functions:
- `archive(*, phase, tmp_path, test_name, artefacts_dir, timestamp)` — copies
  `tmp_path` to `<artefacts_dir>/<timestamp>-<test_name>/` when `phase=="call"`
  and `artefacts_dir` is set.
- `current_timestamp()` — returns a `YYYYMMDD-HHMMSS` string.

`spec/conftest.py` wires these into a `pytest_runtest_makereport` hook that
fires after every test.

The artefact folder is a copy of `tmp_path`. `critique.md` must therefore be
written into `tmp_path` *before* `archive` copies it — the same way
`transcript.md` is written there by `Agent.perform()`.

### Where the critic output lives today

`Critic.evaluate()` (in `play/src/critic.py`) raises `AssertionError` on
failure and returns `None` on pass. It does not currently produce a file.
The critic calls `claude -p` and receives a response string internally, but
does not expose or persist it.

### Approved fixtures

`play/tests/fixtures/sample-critique.jsonl` and `sample-critique.md` are
sourced from a real critic run (approval-test style, same pattern as
`sample-transcript.jsonl` / `sample-transcript.md`). Use these to test
that `Transcriber` renders the critic JSONL correctly before wiring it up.

The work will likely involve:
1. Surfacing the critic's raw response so it can be written to `critique.md`.
2. Writing `critique.md` into `tmp_path` from the scenario test or a fixture.
3. Updating `archive` or the hook if needed (test-drive any changes).

## 2. Refactoring pass

Review all production code in `play/src/` and `spec/` and leave it in good
shape before the xdd skill work begins.

## 3. Write the xdd skill

The `play/` harness is committed: `Agent`, `Transcriber`, and JSONL path
computation are in `play/src/`. What remains on the harness side is wiring
`spec/conftest.py` to expose `--agent=real` — this was built and validated
locally but reverted pending the scenario passing.

A real run (before the revert) confirmed all five scorecard checks fail —
the agent lacks the guidance a skill would provide.

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

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
