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

### `spec/` scenarios

```
uv run --directory spec pytest tests
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
