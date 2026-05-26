# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Complete the agentic critic and wire it into the scenario fixture

The critic skeleton is in place. The approach to completing it:

1. **Wire the fixture** — add a `--inspector` CLI option to
   `spec/conftest.py` (ADR 0009). `uv run pytest` keeps using `Auditor`
   by default; `uv run pytest --inspector=critic` uses
   `Critic(claude=ClaudeCli())`. Do not commit this until the critic
   passes.

2. **Watch the critic fail** — run the scenario under both inspectors.
   The critic's failure reveals exactly what the prompt needs to do.

3. **Test-drive the prompt** — use the concrete failure to decide how
   to drive `_build_prompt` in `play/src/critic.py` correctly. The
   prompt must include the scorecard characteristics and instruct claude
   to respond with `PASS: <characteristic>` or `FAIL: <characteristic>`
   per row.

4. **Commit together** — once the critic passes the scenario, commit
   the fixture wiring and the prompt work in one go.

## Starting point

Key files:

- `play/src/critic.py` — `Critic(claude=…).evaluate(*, evidence,
  working_dir, scorecard)`. Builds a rudimentary prompt (paths only),
  calls `claude`, parses `PASS/FAIL: <characteristic>` lines, raises
  `AssertionError(failures)` on any failures.
- `play/src/claude_cli.py` — `ClaudeCli(subprocess=subprocess.run)`.
  Callable: takes a prompt string, invokes `claude --permission-mode
  acceptEdits -p <prompt>`, returns stdout.
- `play/tests/test_doubles/` — `StubbedClaudeCli(response)` and
  `StubbedSubprocess(returncode, stdout, stderr)` for unit tests.
- `play/tests/contract/test_claude_cli.py` — `@pytest.mark.contract`
  test that calls the real CLI; run with `-m contract`.
- `spec/conftest.py` — `inspector` fixture supplying `Auditor()`.
- `spec/tests/test_red_green_commit.py` — the scenario; scorecard rows
  use `verify(transcript, working_dir)` lambdas that close over `task`.

## Deferred

The "live constraint once the agent is real" — transient artefacts
(`.venv/`, `.pytest_cache/`, `__pycache__/`) polluting the
workspace; agent's cwd needing to be the workspace root — returns
when swapping `_fake_agent_performs` for `claude -p` becomes the
immediate next step.
