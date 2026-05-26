# Commands

Key developer commands for this repo.

## Linting

Ruff must be run from within each project directory.

```
cd play && uv run ruff check .
cd spec && uv run ruff check .
```

## Tests

### `play/` unit tests

```
cd play && uv run pytest
```

### `play/` contract tests (require `claude` CLI)

```
cd play && uv run pytest -m contract
```

### `spec/` scenarios

```
cd spec && uv run pytest
```
