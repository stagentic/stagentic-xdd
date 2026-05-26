# Commands

Key developer commands for this repo. All commands run from the repo root.

## Linting

```
uv run --project play ruff check play
uv run --project spec ruff check spec
```

## Tests

### `play/` unit tests

```
uv run --project play pytest play/tests -m "not contract and not integration"
```

### `play/` integration tests (require `claude` CLI)

```
uv run --project play pytest play/tests -m integration
```

### `play/` contract tests (require `claude` CLI)

```
uv run --project play pytest play/tests -m contract
```

### `spec/` scenarios

```
uv run --project spec pytest spec/tests
```

### `spec/` scenarios with critic (require `claude` CLI)

```
uv run --project spec pytest spec/tests --inspector=critic
```
