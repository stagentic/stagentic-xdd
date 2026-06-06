# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## 1. Refactoring pass

Review all production code in `play/src/` and `spec/` and leave it in good
shape before the xdd skill work begins. Work through each file in turn —
for each production file, review the test first, then the implementation,
and bring both to the same standard.

`claude_cli.py`, `claude_session.py`, `agent.py` are the current reference standard for this repo's production code.
`TestClaudeJsonlPath`, `TestClaudeSession`, `TestAgent` are the current reference standard for tests.

The conventions in `docs/architecture/conventions/` are the standard;
the reference-standard files above are exemplars, not infallible. A
file under review may already exceed them in places. Anchor each
proposed change on the convention text and judgement, not on what
other files happen to do.

Some unchecked boxes link to a per-file punch list at `docs/architecture/improvements/<file>.md` — items tracked separately so they don't bury NEXT.md.

### `play/src/`

- [x] `agent.py` (and `tests/test_agent.py`)
- [x] `fake_agent.py` (and `tests/test_fake_agent.py`)
- [x] `claude_cli.py` (and `tests/test_claude_cli.py`, `tests/contract/test_claude_cli.py`)
- [x] `claude_session.py` (and `tests/test_claude_session.py`)
- [x] `auditor.py` (and `tests/test_auditor.py`)
- [x] `critic.py` (and `tests/test_critic.py`, `tests/integration/test_critic_integration.py`)
- [ ] `scorecard_results.py` (and `tests/test_scorecard_results.py`)
  - Outstanding improvements tracked in
    [`docs/architecture/improvements/scorecard_results.md`](docs/architecture/improvements/scorecard_results.md).
- [ ] `transcriber.py` (and `tests/test_transcriber.py`)

A cross-cutting improvement surfaced by the critic extraction — a
`ScorecardEntry` type spanning `Critic`, `Auditor`, and `formatted_failures_for`
— is deferred and tracked in
[`docs/architecture/improvements/scorecard-entry.md`](docs/architecture/improvements/scorecard-entry.md).

### `spec/`

- [ ] `archiver.py` (and `tests/test_archiver.py`)
- [ ] `conftest.py`

## 2. Write the xdd skill

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
- Commit `spec/conftest.py`, `TASK.md`, and
  `0-placeholder/scene/.claude/settings.json` together.

## Future options

- **Critic saves results to a file**: instruct the critic prompt to write
  its scorecard to a specific file (e.g. `scorecard.json`) rather than
  returning JSON in the response text. The file would contain only JSON,
  sidestepping the prose-stripping problem entirely.
- **Mix mechanical and judgement characteristics in one scorecard**:
  the auditor today verifies rows that carry a `verify` lambda; the
  critic today judges rows that carry only prose. A scorecard given
  to the critic could mix both shapes — the critic would judge the
  prose rows and delegate the lambda-bearing rows to the auditor.
  Other routing approaches are possible.

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
