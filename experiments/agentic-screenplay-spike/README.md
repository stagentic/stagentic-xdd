# agentic-screenplay-spike

A spike exploring a Screenplay-style DSL on top of pytest + `claude -p` to drive TDAB (Test-Driven Agentic Behaviours) scenarios.

> **Status: spike, not target shape.**
> Per [ADR 0001](../../docs/architecture/decisions/0001-start-with-tdab-and-vanilla-pytest.md): *"Spikes under `experiments/` are a source of ideas, not a target shape."* Code here is exploratory and pre-dates the pinning decisions in [ADR 0002](../../docs/architecture/decisions/0002-pin-claude-code-cli-version.md) / [ADR 0003](../../docs/architecture/decisions/0003-pin-model-versions.md) — models are hard-coded in the scenarios rather than read from a pin file.

## What's in here

- **`initial/`** — the simpler shape: pytest tests that drive `claude -p` directly via a small `harness.py` and `stagentic_play.py`.
- **`screenplay/`** — a Screenplay-style DSL prototype (`screenplay_core`, `stagentic_play`, an `Ability*` class convention) layered over pytest. Contains three parallel example shapes of the same scenario, each using a different test runner:
  - `tests/` — plain pytest.
  - `decisions_demo-spec/` — pytest-bdd (Gherkin `.ability` files auto-discovered into `Ability*` test classes).
  - `decisions_demo-behave-spec/` — behave (Gherkin `.ability` files, run via a wrapper that patches behave's `.feature` extension to `.ability`).
- **`transcript_renderer.py`** — shared across subtrees; projects Claude's JSONL session transcripts into the markdown form the Then-step scorecards expect.

These example shapes are parallel explorations at different abstraction levels and across different test runners, not stages of one pipeline.

## Prerequisites

- **`uv`** (Python project manager).
- **`claude` CLI** on `PATH`, with API access to `claude-opus-4-7` (agent under test) and `claude-sonnet-4-6` (evaluator) — the models the scenarios currently hard-code (see `initial/test_scenarios.py`).
- **The `stagentic-promptbook` Claude Code plugin enabled** in this repo (`stagentic-promptbook@stagentic` in `.claude/settings.json` — already present). The scenarios invoke a skill provided by the plugin; task prompts and a snapshot of the skill source are bundled in-tree at `fixtures/tasks/` and `fixtures/skills/decisions-demo/`.

## Running

Install the spike's dependencies once. Plain `--extra dev` covers the pytest and pytest-bdd subtrees; the behave subtree additionally needs the `behave-compat` extra:

```sh
uv sync --extra dev                       # pytest + pytest-bdd subtrees
uv sync --extra dev --extra behave-compat # also covers the behave subtree
```

Note that `uv sync` prunes extras you don't request — running `uv sync --extra dev` after a behave-enabled sync will *uninstall* behave.

Each subtree is run from its own folder — each ships its own conftest/ini/wrapper.

### `initial/` subtree (pytest)

```sh
cd initial
uv run pytest -m integration test_scenarios.py
```

Scenarios are marked `@pytest.mark.integration` because each one shells out to real `claude -p` (~30s/scenario, non-deterministic).

### `screenplay/tests/` subtree (pytest)

```sh
cd screenplay
uv run pytest tests/
```

End-to-end against `claude -p` driving the promptbook sibling. Tests are parametrised across four configs (defined in [`screenplay/tests/fixtures/config.py`](screenplay/tests/fixtures/config.py)):

| Config ID | Backend | Inspector |
|---|---|---|
| `stubbed__auditor` | `StubbedAgent` (canned transcript) | `RuntimeAuditor` (in-process Python asserts) |
| `stubbed__critic` | `StubbedAgent` | `ClaudeCliCritic` (`claude -p` scorecard) |
| `real_claude__auditor` | `ClaudeCliAgent` (real `claude -p`) | `RuntimeAuditor` |
| `real_claude__critic` | `ClaudeCliAgent` | `ClaudeCliCritic` |

Filter with `-k` to run a subset:

```sh
# Fast, no API calls — stubbed agent + Python asserts only
uv run pytest tests/ -k stubbed__auditor

# All stubbed configs (no real claude -p invocations)
uv run pytest tests/ -k stubbed

# Only real-claude configs (slow, hits the API)
uv run pytest tests/ -k real_claude

# A single end-to-end config
uv run pytest tests/ -k real_claude__critic
```

The two axes correspond to [ADR 0001](../../docs/architecture/decisions/0001-start-with-tdab-and-vanilla-pytest.md)'s *backend* (stubbed → real `claude -p`) and *inspector* (auditor → critic) layering.

### `screenplay/decisions_demo-spec/` subtree (pytest-bdd)

```sh
cd screenplay
uv run pytest decisions_demo-spec/
```

Reads `.ability` files (Gherkin) from `decisions_demo-spec/behaviours/` and auto-generates an `Ability<Name>` pytest class per ability, with `should_<scenario>` methods per scenario (see `decisions_demo-spec/test_all.py`). The custom `Ability*`/`should_*` discovery is wired in `screenplay/pytest.ini`.

Uses the same four configs as `screenplay/tests/`; `-k` filtering works the same way (e.g. `-k stubbed` for the fast path).

### `screenplay/decisions_demo-behave-spec/` subtree (behave)

Requires the `behave-compat` extra (see Prerequisites).

```sh
cd screenplay
uv run python decisions_demo-behave-spec/bdd-run.py
```

The wrapper exists because behave hard-codes the `.feature` extension in three places, and the spec files here use `.ability`. `bdd-run.py` monkey-patches the relevant points before behave's main runs (see the file's comments for the specifics). Standard behave flags pass through — e.g. `--dry-run`, `-D <name>=<value>`.

## Layout

```
agentic-screenplay-spike/
├── fixtures/                           # in-tree task prompts + snapshot of skill source
│   ├── tasks/                          #   task prompt files referenced by the scenarios
│   └── skills/decisions-demo/          #   snapshot of the workspace source the plugin is built from
├── initial/                            # simpler form: pytest + claude -p
├── screenplay/                         # Screenplay-style DSL prototype
│   ├── tests/                          #   plain pytest example
│   ├── decisions_demo-spec/            #   pytest-bdd example
│   └── decisions_demo-behave-spec/     #   behave example (via wrapper)
├── transcript_renderer.py              # shared JSONL → markdown renderer
├── pyproject.toml
└── uv.lock
```
