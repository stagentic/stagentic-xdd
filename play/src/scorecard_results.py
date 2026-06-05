from dataclasses import dataclass


@dataclass
class ScorecardResults:
    should: list[dict]
    provided_rows: list[dict] = None
    results: list[dict] = None

    @classmethod
    def from_(cls, maybe_results, should):
        if "status" not in maybe_results[0]:
            raise ValueError
        return cls(should=should, results=maybe_results)
