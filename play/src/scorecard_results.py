from dataclasses import dataclass


@dataclass
class ScorecardResults:
    should: list[dict]
    provided_rows: list[dict] = None
    results: list[dict] = None

    @classmethod
    def from_(cls, maybe_results, should):
        if any("status" not in result for result in maybe_results):
            raise ValueError
        return cls(should=should, results=maybe_results)
