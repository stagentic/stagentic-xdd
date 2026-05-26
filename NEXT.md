# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Swap the fake agent for the real claude CLI

`_fake_agent_performs` in `spec/tests/test_red_green_commit.py` copies
a canned `scene/` over the workspace and returns a pre-written
transcript. The end goal is replacing it with a real `claude -p`
invocation.

`play.fake_agent.FakeAgent` has the shape both variants will share:
`FakeAgent(tasks=…).perform(task=name, working_dir=…)` looks up the
task artefact for `name` and runs it in the working directory; the
resulting `transcript.md` path is held on `agent.transcript`. The
variation between fake and real is only the command that interprets
the task — fake runs a shell script, real will run `claude -p` with
a prompt referencing the task.

1. **Introduce the abstraction** — `FakeAgent` exists in `play/`;
   what remains is the spec-side seam.

   a. Wire `FakeAgent` into the spec via an `agent` fixture in
      `spec/conftest.py` (paralleling `inspector`). Each task dir
      holds `scene/`, `fake-task.sh`, and (when the real agent
      lands) `TASK.md`; `FakeAgent` looks up
      `<tasks>/<name>/fake-task.sh`. Asymmetric naming mirrors
      asymmetric roles — `TASK.md` is *the* task; `fake-task.sh`
      is the fake's substitute for processing it.

      Author a `fake-task.sh` for
      `1-first-test-for-miles-to-km-converter` that produces the
      same workspace state and `transcript.md` the canned `scene/`
      supplies today. Adjust `FakeAgent`'s lookup, then replace
      `_fake_agent_performs` at the call site with
      `agent.perform(...)` and `agent.transcript`.

   b. Make the agent injectable via a `--agent` CLI option in
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

## Known constraints

- Transient artefacts (`.venv/`, `.pytest_cache/`, `__pycache__/`) will
  be visible to the real agent in the workspace — decide whether to
  exclude or clean them before the agent runs.
- The agent's cwd must be the workspace root for `uv run pytest` to
  resolve correctly.
