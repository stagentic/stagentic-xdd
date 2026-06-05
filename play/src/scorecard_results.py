from dataclasses import dataclass


@dataclass
class ScorecardResults:
    provided_should: list[dict]
    provided_rows: list[dict]
