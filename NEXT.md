# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## 1. Preserve critic transcript as `critique.md`

When `--.artefacts-dir` is set and `--inspector=critic`, the critic's output
should be saved alongside `transcript.md` as `critique.md` in the same
artefacts folder. Same rendered format as the agent transcript.

## 2. Refactoring pass

Review all production code in `play/src/` and `spec/` and leave it in good
shape before the xdd skill work begins.

## 3. Write the xdd skill

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

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
