# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Swap the fake agent for the real claude CLI

`_fake_agent_performs` in `spec/tests/test_red_green_commit.py` copies
a canned `scene/` over the workspace and returns a pre-written
transcript. The end goal is replacing it with a real `claude -p`
invocation.

Follow the same pattern used for the critic:

1. **Introduce the abstraction** — there is no concept of "an agent"
   yet, only the private helper `_fake_agent_performs`. Make that
   absence good first: name the role, then add the seam that lets
   it be injected. Both sub-steps land green with only the fake
   implementation present. *(Make the change easy before making the
   easy change — the hard part here is conceptual, not behavioural.)*

   a. Lift `_fake_agent_performs` to a named *agent* role with one
      implementation (a fake, in `play/`). The scenario reaches it
      the same way it currently reaches `inspector`.

   b. Make the agent injectable at runtime via a pytest fixture
      (paralleling the `inspector` fixture) and a `--agent` CLI
      option in `spec/conftest.py`. Only the fake is wired; `real`
      is not yet a valid choice.
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

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
