# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## 1. Refactoring pass

Review all production code in `play/src/` and `spec/` and leave it in good
shape before the xdd skill work begins. Work through each file in turn —
for each production file, review its tests alongside it.

`claude_cli.py` and `claude_session.py` are the current gold standard.
`TestClaudeJsonlPath` and `TestClaudeSession` are the gold standard for tests.

Work through each remaining file in turn — for each production file, review
its tests alongside it and bring them to the same standard.

### `play/src/`

- [ ] `agent.py` (and `tests/test_agent.py`)
- [ ] `auditor.py` (and `tests/test_auditor.py`)
- [x] `claude_cli.py` (and `tests/test_claude_cli.py`, `tests/contract/test_claude_cli.py`)
- [x] `claude_session.py` (and `tests/test_claude_session.py`)
- [ ] `critic.py` (and `tests/test_critic.py`, `tests/integration/test_critic_integration.py`)
- [ ] `fake_agent.py` (and `tests/test_fake_agent.py`)
- [ ] `transcriber.py` (and `tests/test_transcriber.py`)

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

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
