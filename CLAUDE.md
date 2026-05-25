# stagentic-xdd

A planned Claude plugin for language-agnostic BDD/TDD ("XDD"). Initial focus
is the **inner loop** (Red-Green-Refactor) for Python; the outer loop and
additional language adapters are deferred.

See `README.md` for the framing and the link to the longer "what almost
everyone gets wrong about TDD/BDD" argument.

## Where to look first

- `docs/architecture/decisions/` — architectural directions. Accepted
  ones must be adhered to; proposed ones are still under evaluation.
- `NEXT.md` (repo root, if present) — the immediate next step,
  including known constraints. Read it at session start. If a user
  prompt is open-ended ("let's continue", "what next?"), use NEXT.md
  to orient and propose steps. If NEXT.md is missing, ask the user
  what they want to work on.
- `docs/architecture/conventions/` — naming and design-intent
  conventions that should persist across refactors. Consult when
  touching the affected area (e.g. `spec-conventions.md` before
  refactoring or renaming inside `spec/`).
- `docs/writing-style.md` — prose conventions (label-agnostic
  framing; quote actual stated reasons). Consult when writing
  commits, ADRs, or doc bodies.

NEXT.md is not a backlog. When a step from it lands, propose updating
it to reflect the new state — delete what's done, surface what's next.
When a NEXT.md item crystallises into an architectural direction
(proposed or accepted), migrate it to an ADR and replace it with what
comes after.

## Development pattern: TDAB

This plugin is developed using **TDAB** (Test-Driven Agentic Behaviours):
each new agent behaviour is specified as a scenario, exercised against a
fixture, and evaluated against a scorecard rubric (because agent behaviour
is non-deterministic and resists ordinary assertions).

The bootstrap approach is fixed in
`docs/architecture/decisions/0001-start-with-tdab-and-vanilla-pytest.md`:

- Vanilla pytest from day one — no DSL, no framework abstractions yet.
- Stub the agent first, then swap in `claude -p` once the harness is green.
- Then-step evolves *Auditor* (in-process Python asserts) → *Critic*
  (`claude -p` running a scorecard prompt), selected by pytest fixture.
- Framework code (`stagentic-play`) emerges in green-only refactoring, not
  upfront. Spikes under `experiments/` are a source of ideas, not a target
  shape.

## Layout

- `spec/` — pytest project that holds the TDAB scenarios for the xdd skill.
  - `spec/tests/` — one pytest test per scenario.
  - `spec/tasks/<n>-<slug>/` — a task is a unit of agent work. Its
    `scene/` directory holds the canned workspace state after the
    task completes. See ADR 0007 for the chain pattern.
- `play/` — the in-repo embryo of `stagentic-play` (ADR 0001 §33).
  Framework code — currently `Auditor` — that scenarios reach via
  the `inspector` pytest fixture. Has its own pyproject.toml and
  unit-test suite.
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
2. Calls `_fake_agent_performs(task=…, workspace=…)`, which copies
   the target task's `scene/` over the workspace and returns the
   transcript path.
3. Calls `inspector.evaluate(evidence=transcript, scorecard=_have(...))`
   to evaluate a scorecard of `{characteristic, verify, failure}` dicts
   against the transcript. `inspector` is a pytest fixture (in
   `spec/conftest.py`) supplying an `Auditor` from `play/`.

Each `tasks/N-name/scene/` is also the starting fixture for task
`N+1`; `0-placeholder/` is the genesis. Adding a scenario means adding
the next task directory.

Each `scene/` is itself a runnable Python project — `uv sync && uv
run pytest tests/` at the scene root works. Conventions:

- `pyproject.toml` at scene root with
  `[tool.pytest.ini_options] pythonpath = ["src"]` and
  `[tool.uv] package = false`.
- `uv.lock` committed for deterministic `uv sync`.
- Production code lives in `src/`, tests in `tests/`; tests
  import directly (e.g. `from conversion import miles_to_km`,
  no `src.` prefix).

`0-placeholder/scene/` carries the same `pyproject.toml` and
`uv.lock` (byte-identical copies) so the agent's `uv run` in the
inherited workspace lands in the scene's own project rather than
walking up to `spec/pyproject.toml`. Project setup is shared
infrastructure, not something each task produces.

See ADR 0007 for the rationale behind the task chain, the scorecard
shape, and the planned auditor → critic and fake → real agent swaps.
See `docs/architecture/conventions/spec-conventions.md` for naming and
design-intent conventions that should persist across refactors
(`transcript`, `working_dir`).

## Documentation style

In-repo docs (READMEs, ADRs, CLAUDE.md, etc.) describe the system as it stands now. Do not narrate transitions from earlier states — phrases like *"no longer needs X"*, *"used to depend on Y"*, *"X has been removed"* are wrong shape. New readers land on the current version with no knowledge of prior states; transition language is meaningful only to someone reading the git log.

Ask: *"would this sentence make sense to a reader who has never seen any previous version of this file?"* If a clause references a previous state to contextualise the current one, delete it — the current state stands on its own.

Docs must be environment-agnostic. Describe mechanisms in terms of files, commands, and Claude Code features — never in terms of a specific environment (containers, host OS, install method, directory layout, etc.). A reader on any setup should find the docs accurate.

See `docs/writing-style.md` for label-agnostic framing rules (do not reach for "BDD-flavoured", "Gherkin-style", etc.) and the discipline of quoting actual stated reasons in commit bodies and ADRs.

## Commit message style

A commit message answers *why*, not *what* — the diff already records every edited line. The message earns its place by stating the motivating problem, constraint, or goal the change serves.

**Subjects:** declarative, framed as what the change makes true. Cast as a completion of *"After this commit, …"* — e.g. `pytest --collect-only allowed on any test path`. Imperative voice (`add X`, `remove Y`) and mechanism-narrating phrases (`X directive added`, `Y section removed`) are wrong shape.

**Bodies:** motivation first. Brief supporting detail on mechanism is fine, but only after the why is clear.

**Format:** conventional commits — `<type>(<scope>): <subject>`.

**ADR commits:** layer the ADR status immediately after the type/scope prefix:
- `Status: Proposed` → `docs(adr): proposal: <subject>`
- `Status: Accepted` → `docs(adr): decision: <subject>`
- Other statuses (Rejected, Superseded, Deprecated) — use the status word by analogy.

**Commit proposals:** when proposing a commit for approval, always show the
complete message verbatim — subject, blank line, body (if any), blank line,
and trailer — exactly as it will be passed to `git commit -m`.

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

