# Commands

Key developer commands for this repo. All commands run from the repo root.

## Linting

```
uv run --directory play ruff check .
uv run --directory spec ruff check .
```

## Tests

### `play/` unit tests

```
uv run --directory play pytest tests -m "not contract and not integration"
```

### `play/` integration tests (require `claude` CLI)

```
uv run --directory play pytest tests -m integration
```

### `play/` contract tests (require `claude` CLI)

```
uv run --directory play pytest tests -m contract
```

### `play/` full suite (require `claude` CLI)

```
uv run --directory play pytest
```

### `spec/` scenarios

```
uv run --directory spec pytest tests
```

### `spec/` scenarios with critic, preserving artefacts (require `claude` CLI)

```
uv run --directory spec pytest tests --inspector=critic --.artefacts-dir .artefacts
```

### `spec/` scenarios with real agent (require `claude` CLI)

> Not yet available — lands once the scenario passes with the real agent.

```
uv run --directory spec pytest tests --agent=real
```

### `spec/` scenarios with real agent, preserving artefacts (require `claude` CLI)

> Not yet available — lands once the scenario passes with the real agent.

```
uv run --directory spec pytest tests --agent=real --.artefacts-dir .artefacts
```

### `spec/` scenarios with critic (require `claude` CLI)

```
uv run --directory spec pytest tests --inspector=critic
```

### `spec/` scenarios with real agent and critic (require `claude` CLI)

> Not yet available — lands once the scenario passes with the real agent.

```
uv run --directory spec pytest tests --agent=real --inspector=critic
```

## Mutation testing

Mutates the files in `source_paths` (`play/pyproject.toml`) against the fast
unit lane. See ADR [0010](docs/architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md).

### Focus one file (during TDD or review)

```
uv run --directory play mutmut run "<file>*"
```

`<file>` is the module name, e.g. `critic`.

### Full set (before work is 'done')

```
uv run --directory play mutmut run
```

### Inspect survivors

```
uv run --directory play mutmut results
uv run --directory play mutmut show <mutant>
```

After a test-only change, remove `mutants/` before re-running — mutmut caches by
mutated source and otherwise replays stale results:

```
rm -rf play/mutants
```
