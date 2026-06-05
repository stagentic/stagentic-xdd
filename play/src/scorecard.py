def formatted_failures_for(failures: list[dict[str, str]]) -> str:
    return "\n".join(f"- {row['characteristic']}: {row['failure']}" for row in failures)
