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

## Working agreements

- This repo sits under `/workspace`; the policies in `/workspace/CLAUDE.md`
  apply (authorisation before executing on plans, "commit" means propose,
  concise replies, etc.). Nothing here overrides them.
- Pushing to GitHub is not configured in this container — surface the
  exact `git push …` command for the user to run on their host.
