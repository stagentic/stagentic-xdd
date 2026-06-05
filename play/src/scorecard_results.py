from dataclasses import dataclass


@dataclass
class ScorecardResults:
    provided_should: list[dict]
    provided_rows: list[dict] = None
    results: list[dict] = None

    @classmethod
    def from_(cls, maybe_results, should):
        return cls(provided_should=should, results=maybe_results)
