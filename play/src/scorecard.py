def formatted_failures_for(failures: list[dict[str, str]]) -> str:
    return f"- {failures[0]['characteristic']}: {failures[0]['failure']}"
