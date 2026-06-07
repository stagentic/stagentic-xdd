# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## 1. `test_utilities` project (ADR 0012) — Phase 1 done, Phase 2 remaining

**Phase 1 done** (committed): shared `matchers` now live in `test_utilities/src`,
a project peer to `play`/`spec`, with their own tests and a permanent mutation
gate; `play` reaches them via a relative `pythonpath`. `contains_strings` was
hardened by TDD in its new home (requires every substring, mutation-clean) and
wired into `test_critic_integration.py` as the first cross-project consumer.
`CLAUDE.md` "Layout", `COMMANDS.md`, and `working-practices.md` are updated for
the new project.

**Phase 2 — make `test_utilities` an installable package.** A uv workspace
member that `play`/`spec` declare as a dependency, retiring the relative
`pythonpath`. Bigger than Phase 1: there is no workspace root today and both
`play` and `spec` are standalone (`package = false`), so this introduces a root
workspace, flips both to members sharing one lockfile, and gives
`test_utilities` a build backend. A dependency/lockfile change means each
project's host `.venv-jb` must be re-synced on the host afterwards.

**Later helpers to home here (ADR 0012 scope):** `case` (consolidate the three
definitions across two signatures into one) and `does_not_raise`.

**Follow-on idea — a `contains_none_of` matcher.** Asserts *none* of the given
substrings appear, for collapsing repeated `does_not(contain_string(...))`
checks into one. Mind the De Morgan trap: `does_not(contains_strings(a, b))` is
`is_not(all_of(...))` = "at least one absent", **not** "all absent". The
all-absent form is `is_not(any_of(contain_string …))` (≡
`all_of(does_not(contain_string …))`), which reports a combined failure message
rather than independent ones. TDD it in `test_utilities`, mirroring the
`contains_strings` rhythm.

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
