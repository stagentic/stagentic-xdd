# agentic-screenplay-spike

A spike exploring a Screenplay-style DSL on top of pytest + `claude -p` to drive TDAB (Test-Driven Agentic Behaviours) scenarios.

> **Status: spike, not target shape.**
> Per [ADR 0001](../../docs/architecture/decisions/0001-start-with-tdab-and-vanilla-pytest.md): *"Spikes under `experiments/` are a source of ideas, not a target shape."* Code here is exploratory and pre-dates the pinning decisions in [ADR 0002](../../docs/architecture/decisions/0002-pin-claude-code-cli-version.md) / [ADR 0003](../../docs/architecture/decisions/0003-pin-model-versions.md) — models are hard-coded in the scenarios rather than read from a pin file.

## What's in here

- **`initial/`** — the simpler shape: pytest tests that drive `claude -p` directly via a small `harness.py` and `stagentic_play.py`.
- **`screenplay/`** — a Screenplay-style DSL prototype (`screenplay_core`, `stagentic_play`, an `Ability*` class convention) layered over pytest.
- **`transcript_renderer.py`** — shared between the two subtrees; projects Claude's JSONL session transcripts into the markdown form the Then-step scorecards expect.

The two subtrees are parallel explorations of the same problem at different abstraction levels, not stages of one pipeline.

## Prerequisites

- **`uv`** (Python project manager).
- **`claude` CLI** on `PATH`, with API access to `claude-opus-4-7` (agent under test) and `claude-sonnet-4-6` (evaluator) — the models the scenarios currently hard-code (see `initial/test_scenarios.py`).
- **A sibling checkout of `stagentic-promptbook`** next to this repo. The harness walks up from its own location to find a sibling `stagentic-promptbook/` directory and uses it as the agent's working directory; runs fail if it's missing.

## Running

Install the spike's dev dependencies once:

```sh
uv sync --extra dev
```

Each subtree is run with its own folder as the pytest working directory — each ships its own `conftest.py` (and `screenplay/` has its own `pytest.ini` with custom `Ability*`/`should_*` naming).

### `initial/` subtree

```sh
cd initial
uv run pytest -m integration test_scenarios.py
```

Scenarios are marked `@pytest.mark.integration` because each one shells out to real `claude -p` (~30s/scenario, non-deterministic).

### `screenplay/` subtree

```sh
cd screenplay
uv run pytest tests/
```

Same caveats as above — end-to-end against `claude -p` driving the promptbook sibling.

Tests are parametrised across four configs (defined in [`screenplay/tests/fixtures/config.py`](screenplay/tests/fixtures/config.py)):

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

## Layout

```
agentic-screenplay-spike/
├── initial/                 # simpler form: pytest + claude -p
├── screenplay/              # Screenplay-style DSL prototype
├── transcript_renderer.py   # shared JSONL → markdown renderer
├── pyproject.toml
└── uv.lock
```
