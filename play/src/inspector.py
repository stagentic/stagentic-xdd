from pathlib import Path
from typing import Any, Protocol


class Inspector(Protocol):
    def evaluate(self, *, evidence_source: Path, working_dir: Path, should: list[Any]) -> None: ...
