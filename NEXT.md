# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## 1. Stand up the `test_utilities` project (ADR 0012) — current focus

Implement ADR
[0012](docs/architecture/decisions/0012-home-shared-test-utilities-in-a-dedicated-project.md)
(Proposed): move shared test helpers (`matchers`; later `case`,
`does_not_raise`) into a `test_utilities` project peer to `play`/`spec`, so they
gain their own tests and mutation coverage. mutmut can't mutate a helper under
`tests/` — its source roots (`.`, `src`, `source`) are hardcoded — which is why
the move is needed.

**Uncommitted working-tree state to resolve first:**
- `play/tests/matchers.py`, `play/tests/test_matchers.py` — in-progress
  `contains_strings` hardening (2nd test + `contain_string(substrings[-1])`
  impl) on top of the committed fake-it (`anything()`) state (commit `4f4b39a`).
- `play/pyproject.toml` — a temporary `source_paths` addition of
  `tests/matchers.py` that does **not** work (see ADR 0012); revert it.

**Sequence:**
1. Revert the WIP on `matchers.py`/`test_matchers.py` to their committed
   fake-it state, and revert the `play/pyproject` `source_paths` change — so the
   move is a clean structural rename. (The hardening gets redone via TDD in the
   new home, where mutation works.)
2. **Structural:** create `test_utilities/` (`pyproject.toml` mirroring `play`'s;
   `src/`, `tests/`). `git mv` `matchers.py` → `test_utilities/src/` and
   `test_matchers.py` → `test_utilities/tests/`. Add `"../test_utilities/src"`
   to `play`'s (and `spec`'s, if it imports `matchers`) pytest `pythonpath`.
   `test_utilities` carries its own `[tool.mutmut] source_paths =
   ["src/matchers.py"]`. Commit.
3. Finish the `contains_strings` TDD in `test_utilities` (add the "first
   substring missing" test → `all_of(contain_string …)` impl), mutation-verified
   after each green (`mutmut run "matchers*"`).
4. Wire `contains_strings` into `test_critic_integration.py` (the two positive
   `contains_string` calls → one `contains_strings`); green + committed →
   **Phase 1 done**.
5. **Phase 2:** convert `test_utilities` to a proper installable package (uv
   workspace member that `play`/`spec` depend on), retiring the relative
   `pythonpath`.

**Docs to update as this lands:** `CLAUDE.md` "Layout" (new project),
`COMMANDS.md` (its test/lint/mutmut commands), and the working-practices
"add the file you're developing to `source_paths`" wording → point shared
helpers at `test_utilities`.

## 2. Improvement plan

We are working through each file in turn, bringing each up to the reference
standard set by `critic.py` / `TestCritic` — matching the conventions inferred
from `critic.py` and `test_critic.py` — and running mutation testing to confirm
coverage.

`critic.py` is the current reference standard for this repo's production code.
`TestCritic` is the current reference standard for tests.

For each file:
- Review the test first, then the implementation; bring both to the standard
  set by `critic.py` / `test_critic.py`.
- Match the conventions inferred from those files, alongside the documented
  conventions in `docs/architecture/conventions/`.
- Run mutation testing (`mutmut`, per ADR
  [0010](docs/architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md)):
  review survivors against the tests and act where appropriate. Read-only for now (ADR 0010 stage 1); "where
  appropriate" is judgement, not an enforced gate. `source_paths` grows by one
  file as each reaches acceptable coverage.

The conventions in `docs/architecture/conventions/` are the standard; the
reference-standard files above are exemplars, not infallible. A file under
review may already exceed them in places. Anchor each proposed change on the
convention text and judgement, not on what other files happen to do. Follow
the working practices in [`docs/working-practices.md`](docs/working-practices.md)
for the workflow itself, rather than inferring one from the files.

Some files have a per-file punch list at
`docs/architecture/improvements/<file>.md` — items tracked separately so they
don't bury NEXT.md.

### `play/src/`

- [x] `critic.py` (and `tests/test_critic.py`, `tests/integration/test_critic_integration.py`)
- [ ] `agent.py` (and `tests/test_agent.py`)
- [ ] `fake_agent.py` (and `tests/test_fake_agent.py`)
- [ ] `claude_cli.py` (and `tests/test_claude_cli.py`, `tests/contract/test_claude_cli.py`)
- [ ] `claude_session.py` (and `tests/test_claude_session.py`)
- [ ] `auditor.py` (and `tests/test_auditor.py`)
- [ ] `scorecard_results.py` (and `tests/test_scorecard_results.py`)
  - Outstanding improvements tracked in
    [`docs/architecture/improvements/scorecard_results.md`](docs/architecture/improvements/scorecard_results.md).
- [ ] `transcriber.py` (and `tests/test_transcriber.py`)
- [ ] `claude_jsonl_path.py` (and `tests/test_claude_jsonl_path.py`)
- [ ] `failure_message.py` (and `tests/test_failure_message.py`)
- [ ] `raise_if.py` (and `tests/test_raise_if.py`)
- [ ] `scorecard_json_extraction.py` (and `tests/test_scorecard_json_extraction.py`)
- [ ] `inspector.py` — No test yet

A cross-cutting improvement surfaced by the critic extraction — a
`ScorecardEntry` type spanning `Critic`, `Auditor`, and `formatted_failures_for`
— is deferred and tracked in
[`docs/architecture/improvements/scorecard-entry.md`](docs/architecture/improvements/scorecard-entry.md).

### `spec/`

- [ ] `archiver.py` (and `tests/test_archiver.py`)
- [ ] `conftest.py`

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
