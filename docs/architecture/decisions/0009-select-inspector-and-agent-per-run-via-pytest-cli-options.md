---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0009 — Select inspector and agent per run via pytest CLI options

**Status:** Accepted

## Context

Scenario tests in `spec/` have two configuration axes:

- **Inspector** — who evaluates the scorecard: `Auditor` (deterministic, in-process) or `Critic` (`claude -p`, non-deterministic).
- **Agent** — who performs the task: the fake agent (a `copytree` stub) or the real agent (`claude -p`).

This gives three meaningful run configurations, executed in progression:

1. Fake agent + Auditor — fast, deterministic; validates harness wiring.
2. Fake agent + Critic — introduces LLM evaluation; validates the critic prompt.
3. Real agent + Critic — full end-to-end; validates agent behaviour.

Each run must be independently invocable and produce a clean, isolated result — one configuration per run. The output must make it immediately clear which configuration is under test and which configuration is broken, without test results from different configurations appearing interleaved in the same run.

pytest fixture parametrisation is not suitable: it runs each test once per parameter value within a single run, interleaving configurations in the output and making it harder to see which configuration is failing.

## Decision

Register custom pytest CLI options — `--inspector` and `--agent` — in `spec/conftest.py`. The `inspector` fixture (and, when the real agent lands, an `agent` fixture) reads the option and returns the appropriate implementation.

Defaults make the fast deterministic run require no flags:

```
uv run pytest                                    # fake agent + auditor (default)
uv run pytest --inspector=critic                 # fake agent + critic
uv run pytest --inspector=critic --agent=real    # real agent + critic
```

The `inspector` fixture shape:

```python
def pytest_addoption(parser):
    parser.addoption("--inspector", default="auditor", choices=["auditor", "critic"])

@pytest.fixture
def inspector(request):
    match request.config.getoption("--inspector"):
        case "auditor":
            return Auditor()
        case "critic":
            return Critic(claude=ClaudeCli())
```

The `--agent` option follows the same pattern when the real agent is introduced.

## Consequences

- Each run produces a single-configuration result. A failing critic run shows only critic failures; a passing auditor run confirms only that the harness wiring is correct.
- Progression through configurations is explicit at the command line, visible in shell history, and documentable in `COMMANDS.md`.
- The `inspector` fixture becomes a one-liner dispatch; no parametrisation machinery in the test body.
- The default (`auditor`) means `uv run pytest` without flags always gives the fast loop — the one most run during development.
- Adding a fourth configuration axis in future follows the same pattern without touching existing test bodies.
- The `--agent=real` flag is not implemented until the real agent lands; the option is introduced at that point, not speculatively now.

## Alternatives considered

- **pytest fixture parametrisation** (`@pytest.fixture(params=[Auditor, Critic])`): runs all configs in one go, interleaved per test. Rejected: makes it hard to see which configuration is broken; does not support the "run one config, fix it, move on" workflow.
- **Environment variables** (`INSPECTOR=critic uv run pytest`): simpler to implement, but invisible in pytest's output header and not self-documenting in shell history.
- **Separate `pyproject.toml` profiles or ini files**: each config gets its own invocation target. More setup overhead; the custom option achieves the same isolation with less machinery.
- **pytest marks** (`-m critic`): marks select *tests*, not *fixture implementations*. Using them to select configuration conflates test selection with test configuration.
