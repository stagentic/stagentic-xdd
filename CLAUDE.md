# stagentic-xdd

A planned Claude plugin for language-agnostic BDD/TDD ("XDD"). Initial focus
is the **inner loop** (Red-Green-Refactor) for Python; the outer loop and
additional language adapters are deferred.

See `README.md` for the framing and the link to the longer "what almost
everyone gets wrong about TDD/BDD" argument.

## Where to look first

Read these thoroughly when relevant; don't rely on the one-line summary alone:

- `docs/architecture/decisions/` — architectural directions. Accepted
  ones must be adhered to; proposed ones are still under evaluation.
- `NEXT.md` (repo root, if present) — the immediate next step,
  including known constraints. Read it at session start. If a user
  prompt is open-ended ("let's continue", "what next?"), use NEXT.md
  to orient and propose steps. If NEXT.md is missing, ask the user
  what they want to work on.
- `COMMANDS.md` (repo root) — key developer commands (test runners, linter).
- `docs/architecture/conventions/` — naming and design-intent
  conventions that should persist across refactors. Consult when
  touching the affected area:
  - `test-conventions.md` — test shape for `play/tests/`.
  - `src-conventions.md` — production code style for `play/src/`.
  - `spec-conventions.md` — structures and naming intent for `spec/`.
- `docs/writing-style.md` — prose conventions (label-agnostic
  framing; quote actual stated reasons). Consult when writing
  commits, ADRs, or doc bodies.
- `docs/commit-style.md` — commit subject/body shape, conventional-commits
  format, ADR-commit layering, commit-proposal format.
- `docs/document-style.md` — in-repo doc conventions (current-state framing,
  environment-agnostic mechanisms).
- `docs/working-practices.md` — workflow practices: lead with the
  proposed commit; separate behavioural from structural changes.

NEXT.md is not a backlog. When a step from it lands, propose updating
it to reflect the new state — delete what's done, surface what's next.
When a NEXT.md item crystallises into an architectural direction
(proposed or accepted), migrate it to an ADR and replace it with what
comes after.

## Development pattern: TDAB

This plugin is developed using **TDAB** (Test-Driven Agentic Behaviours).
The approach is explained in ADR 0001
(`docs/architecture/decisions/0001-start-with-tdab-and-vanilla-pytest.md`).

## Layout

- `spec/` — pytest project that holds the TDAB scenarios for the xdd skill.
  - `spec/tests/` — one pytest test per scenario.
  - `spec/tasks/<n>-<slug>/` — a task is a unit of agent work. Its
    `scene/` directory holds the canned workspace state after the
    task completes. See ADR 0007 for the chain pattern.
- `play/` — the in-repo embryo of `stagentic-play` (ADR 0001 §33).
  Framework code — `Agent`, `FakeAgent`, `Transcriber`, `Auditor`, `Critic`,
  `ClaudeSession`, `ClaudeCli`, and `Inspector` — that scenarios reach via pytest fixtures. Has its own
  pyproject.toml and unit-test suite. Test doubles live in
  `play/tests/test_doubles/`; contract tests (marked `contract`) live in
  `play/tests/contract/`; integration tests (marked `integration`) live in
  `play/tests/integration/`.
- `experiments/` — spikes. `agentic-screenplay-spike/` prototypes a
  Screenplay-style DSL on pytest + `claude -p`; do **not** treat it as a
  target architecture.
- `docs/architecture/decisions/` — ADRs. Append-only, one decision per
  numbered file. Start from `TEMPLATE.md`.
- `docs/assets/` — diagrams referenced from `README.md`.
- `.claude/settings.json` — checked-in Claude Code config: shared
  permissions, pinned model env vars (ADR 0003), and
  `DISABLE_AUTOUPDATER` (ADR 0002).

## Working with `spec/`

A scenario in `spec/tests/test_*.py` does three things:

1. Copies the previous task's `scene/` into a tmp workspace.
2. Calls `agent.perform(task=…, working_dir=…)` via the `agent` pytest
   fixture (in `spec/conftest.py`). The fixture currently exposes only
   `FakeAgent`; `--agent=real` is not yet wired up — it lands once the
   xdd skill has its first passing scenario.
3. Calls `inspector.evaluate(evidence=agent.transcript, working_dir=working_dir,
   should=_have(...))` to evaluate a scorecard against the transcript.
   `inspector` is a pytest fixture (in `spec/conftest.py`) supplying an
   inspector from `play/`. Auditor scorecard rows carry
   `{characteristic, verify, failure}`; `verify` is Auditor-specific.
   Critic rows need only `{characteristic, failure}`.

Each `tasks/N-name/scene/` is also the starting fixture for task
`N+1`; `0-placeholder/` is the genesis. Adding a scenario means adding
the next task directory.

See ADR 0007 for the task-chain rationale and the planned
auditor → critic and fake → real agent swaps. See
`docs/architecture/conventions/spec-conventions.md` for spec
conventions (`transcript`, `working_dir`, scene projects).

## Relevant test suites

### Full baseline

Default suite. Run at the start of every new session, and any time the
"Change in `play/` beyond a single test file" rule applies. Issue as
separate tool calls in a single message so they run concurrently.

- [`play/` full suite](COMMANDS.md#play-full-suite-require-claude-cli)
- [`play/` integration tests](COMMANDS.md#play-integration-tests-require-claude-cli) — hit real claude; called out explicitly
- [`spec/` scenarios](COMMANDS.md#spec-scenarios) — fake agent, auditor (default)
- [`spec/` scenarios with critic](COMMANDS.md#spec-scenarios-with-critic-require-claude-cli) — fake agent, real critic
- Real agent excluded while the xdd skill is in development.

### Before any commit

Whether proposing one or making one autonomously, run the tests relevant to the change:

- **Single `test_`-prefixed file changed alone**: run only that file
  (e.g. `uv run --directory play pytest tests/test_critic.py`).
  Test infrastructure changes (conftest, fixtures, shared doubles)
  don't qualify — they can affect every test, so the wider rule applies.
- **Expand-contract introductions** — new code not yet integrated with anything
  else (e.g. a new test double, a new utility): run its isolated test file only.
- **Change in `spec/` beyond a single test file** — production code, multiple
  test files, or test infrastructure: run spec configurations in parallel:
  - [`spec/` scenarios](COMMANDS.md#spec-scenarios) — fake agent, auditor (default)
  - [`spec/` scenarios with critic](COMMANDS.md#spec-scenarios-with-critic-require-claude-cli) — fake agent, real critic
- **Change in `play/` beyond a single test file** (or anything integrated):
  the [Full baseline](#full-baseline).

## ADR conventions

- **Portability rule:** ADRs must not link to files outside this
  repository. Intra-repo links and external web URLs are fine. The rule is
  carried in each ADR's frontmatter `agent-directive` — preserve it when
  editing, and apply it when adding new ADRs. Inline critical context
  rather than linking out.
- Statuses: `Proposed`, `Accepted`, `Rejected`, `Superseded`, `Deprecated`.
  New decisions start as `Proposed` and move to `Accepted` once validated.
- When adding an ADR: copy `TEMPLATE.md` to `NNNN-short-slug.md` (next
  number), fill it in, and add a row to the index in
  `docs/architecture/decisions/README.md`.
- **Keep `CLAUDE.md` in sync:** when adding an ADR or making a material
  change (code, structure, conventions, working agreements), re-read this
  `CLAUDE.md` and *propose changes* to any sections that have gone stale
  or contradict the change. Do not edit `CLAUDE.md` without explicit
  authorisation.

