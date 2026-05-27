from pathlib import Path
from typing import Any, Protocol


class Inspector(Protocol):
    def evaluate(self, *, evidence: Path, working_dir: Path, should: list[Any]) -> None: ...
