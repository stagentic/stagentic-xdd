from dataclasses import dataclass


@dataclass
class ScorecardResult:
    provided_should: list[dict]
    provided_rows: list[dict]
