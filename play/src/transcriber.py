import json
from collections import namedtuple
from datetime import datetime


Block = namedtuple("Block", ["timestamp", "kind", "content"])


class Transcriber:
    def render(self, jsonl_path):
        return "".join(_format(block) for block in _blocks(jsonl_path))


def _blocks(jsonl_path):
    with open(jsonl_path) as f:
        for line in f:
            entry = json.loads(line)
            timestamp = _format_time(entry.get("timestamp", ""))
            content = entry.get("message", {}).get("content", [])
            if isinstance(content, list):
                for item in content:
                    yield _block_from_item(item, timestamp)
            else:
                block = _block_from_entry(entry, timestamp)
                if block:
                    yield block


def _block_from_item(item, timestamp):
    kind = item.get("type", "").upper().replace("_", " ")
    if item.get("type") == "tool_use":
        name = item.get("name", "")
        key = _tool_key(name, item.get("input", {}))
        return Block(timestamp, kind, f"{name} `{key}`")
    return Block(timestamp, kind, item.get("text") or item.get("content") or "")


def _block_from_entry(entry, timestamp):
    kind = entry.get("type", "").upper().replace("_", " ")
    if not kind:
        return None
    content = entry.get("aiTitle") or entry.get("content") or entry.get("operation") or ""
    return Block(timestamp, kind, content)


def _format(block):
    timestamp, kind, content = block
    if not kind:
        return ""
    if kind == "TOOL USE":
        return f"`{timestamp}` [{kind}] {content}\n\n"
    if kind == "TOOL RESULT" and content:
        return f"`{timestamp}` [{kind}]\n\n```\n{content}\n```\n\n"
    if content:
        return f"`{timestamp}` [{kind}]\n\n{content}\n\n"
    return f"`{timestamp}` [{kind}]\n\n"


def _tool_key(name, tool_input):
    key_fields = {"Bash": "command", "Read": "file_path", "Write": "file_path",
                  "Edit": "file_path", "Glob": "pattern", "Grep": "pattern"}
    field = key_fields.get(name)
    if field:
        return tool_input.get(field, "")
    return next(iter(tool_input.values()), "") if tool_input else ""


def _format_time(timestamp):
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%SZ")
    except ValueError:
        return ""
