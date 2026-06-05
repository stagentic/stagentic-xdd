from dataclasses import dataclass

_REQUIRED_KEYS = ("characteristic", "status")


@dataclass
class ScorecardResults:
    should: list[dict]
    provided_rows: list[dict] = None
    results: list[dict] = None

    @classmethod
    def from_(cls, maybe_results, should):
        if any(_is_missing_key_from(result) for result in maybe_results):
            raise ValueError(
                "invalid rows:\n"
                "- missing 'status': {'characteristic': 'runs the test'}"
            )
        return cls(should=should, results=maybe_results)


def _is_missing_key_from(result):
    return any(key not in result for key in _REQUIRED_KEYS)
