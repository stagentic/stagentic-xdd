from dataclasses import dataclass

_REQUIRED_KEYS = ("characteristic", "status")


@dataclass
class ScorecardResults:
    should: list[dict]
    provided_rows: list[dict] = None
    results: list[dict] = None

    @classmethod
    def from_(cls, maybe_results, should):
        results = _results_unless(
            maybe_results,
            has_problem=_invalid,
            raising_error=ValueError,
        )

        characteristics = [result["characteristic"] for result in results]
        duplicated = {name for name in characteristics if characteristics.count(name) > 1}
        if duplicated:
            raise ValueError(
                "duplicated characteristics:\n" + "\n".join(
                    f"- {result['characteristic']}: {result['status']}"
                    for result in results
                    if result["characteristic"] in duplicated
                )
            )

        return cls(should=should, results=results)


def _results_unless(maybe_results, *, has_problem, raising_error):
    problem = has_problem(maybe_results)
    if problem: raise raising_error(problem)
    return maybe_results


def _invalid(maybe_results):
    problems = _problems_in([
        _empty(maybe_results),
        _invalid_rows_in(maybe_results),
    ])
    return _problems_message(problems) if problems else None


def _empty(maybe_results):
    return "results must not be empty" if not maybe_results else None


def _invalid_rows_in(maybe_results):
    results_with_missing_keys = [
        result for result in maybe_results if _is_missing_key_from(result)
    ]
    return _formatted_invalid_results(
        results_with_missing_keys
    ) if results_with_missing_keys else None


def _is_missing_key_from(result):
    return any(
        key not in result for key in _REQUIRED_KEYS
    )


def _formatted_invalid_results(results):
    return "invalid rows:\n" + "\n".join(
        _formatted_invalid_result(result) for result in results
    )


def _formatted_invalid_result(result):
    missing = ", ".join(
        repr(key) for key in _REQUIRED_KEYS if key not in result
    )
    return f"- missing {missing}: {result}"


def _problems_in(possible_problems):
    return [
        problem for problem in possible_problems if problem is not None
    ]


def _problems_message(problems):
    return "\n\n".join(problems)
