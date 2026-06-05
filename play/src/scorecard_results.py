from dataclasses import dataclass

_REQUIRED_KEYS = ("characteristic", "status")


@dataclass
class ScorecardResults:
    should: list[dict]
    provided_rows: list[dict] = None
    results: list[dict] = None

    @classmethod
    def from_(cls, maybe_results, should):
        invalid = [result for result in maybe_results if _is_missing_key_from(result)]
        if invalid:
            raise ValueError(_formatted_invalid_results(invalid))
        return cls(should=should, results=maybe_results)


def _is_missing_key_from(result):
    return any(key not in result for key in _REQUIRED_KEYS)


def _formatted_invalid_results(results):
    return "invalid rows:\n" + "\n".join(
        _formatted_invalid_result(result) for result in results
    )


def _formatted_invalid_result(result):
    missing = ", ".join(
        repr(key) for key in _REQUIRED_KEYS if key not in result
    )
    return f"- missing {missing}: {result}"
