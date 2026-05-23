# stagentic-xdd

A planned Claude plugin for language-agnostic BDD/TDD ("XDD"). Initial focus
is the **inner loop** (Red-Green-Refactor) for Python; the outer loop and
additional language adapters are deferred.

See `README.md` for the framing and the link to the longer "what almost
everyone gets wrong about TDD/BDD" argument.

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

- `docs/architecture/decisions/` — ADRs. Append-only, one decision per
  numbered file. Start from `TEMPLATE.md`.
- `experiments/` — spikes. `agentic-screenplay-spike/` prototypes a
  Screenplay-style DSL on pytest + `claude -p`; do **not** treat it as a
  target architecture.
- `docs/assets/` — diagrams referenced from `README.md`.

There is no top-level Python project yet — `experiments/*/pyproject.toml`
is spike-scoped.

## Documentation style

In-repo docs (READMEs, ADRs, CLAUDE.md, etc.) describe the system as it stands now. Do not narrate transitions from earlier states — phrases like *"no longer needs X"*, *"used to depend on Y"*, *"X has been removed"* are wrong shape. New readers land on the current version with no knowledge of prior states; transition language is meaningful only to someone reading the git log.

Ask: *"would this sentence make sense to a reader who has never seen any previous version of this file?"* If a clause references a previous state to contextualise the current one, delete it — the current state stands on its own.

Docs must be environment-agnostic. Describe mechanisms in terms of files, commands, and Claude Code features — never in terms of a specific environment (containers, host OS, install method, directory layout, etc.). A reader on any setup should find the docs accurate.

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

