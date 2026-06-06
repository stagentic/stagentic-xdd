import json


def candidate_scorecard_from(response: str) -> list[dict]:
    return _decoded_from(_json_text_in(response))


def _decoded_from(json_text: str) -> list[dict]:
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as err:
        raise ValueError(f"response did not contain valid JSON: {json_text!r}") from err


def _json_text_in(result: str) -> str:
    text = result.strip()
    stages = (
        _remove_content_before_json,
        _remove_content_after_json,
    )
    for chisel in stages:
        text = chisel(text)
    return text


def _remove_content_before_json(text: str) -> str:
    start = _start_of_json(text)
    return text if start is None else text[start:]


def _start_of_json(text: str) -> int | None:
    decoder = json.JSONDecoder()
    end = len(text)
    while (start := text.rfind("[", 0, end)) != -1:
        try:
            content, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            end = start
            continue
        if _is_scorecard(content): return start
        end = start
    return None


def _is_scorecard(content) -> bool:
    return isinstance(content, list) and all(
        isinstance(row, dict) and "characteristic" in row and "status" in row
        for row in content
    )


def _remove_content_after_json(text: str) -> str:
    try:
        _, end = json.JSONDecoder().raw_decode(text)
    except json.JSONDecodeError:
        return text
    return text[:end]
