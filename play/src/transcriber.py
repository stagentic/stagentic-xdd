import json
from datetime import datetime


class Transcriber:
    def render(self, jsonl_path):
        parts = []
        with open(jsonl_path) as f:
            for line in f:
                entry = json.loads(line)
                timestamp = _format_time(entry.get("timestamp", ""))
                message = entry.get("message", {})
                content = message.get("content", [])
                if isinstance(content, list):
                    for item in content:
                        rendered = _render_item(item, timestamp)
                        if rendered:
                            parts.append(rendered)
                else:
                    rendered = _render_entry(entry, timestamp)
                    if rendered:
                        parts.append(rendered)
        return "".join(parts)


def _render_item(item, timestamp):
    kind = item.get("type", "").upper().replace("_", " ")
    if item.get("type") == "tool_use":
        name = item.get("name", "")
        key = _tool_key(name, item.get("input", {}))
        return f"`{timestamp}` [{kind}] {name} `{key}`\n\n"
    if item.get("type") == "tool_result":
        content = item.get("content") or ""
        if content:
            return f"`{timestamp}` [{kind}]\n\n```\n{content}\n```\n\n"
        return f"`{timestamp}` [{kind}]\n\n"
    content = item.get("text") or item.get("content") or ""
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


def _render_entry(entry, timestamp):
    kind = entry.get("type", "").upper().replace("_", " ")
    content = entry.get("aiTitle") or entry.get("content") or entry.get("operation") or ""
    if content:
        return f"`{timestamp}` [{kind}] {content}\n\n"
    return f"`{timestamp}` [{kind}]\n\n" if kind else ""


def _format_time(timestamp):
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%SZ")
    except ValueError:
        return ""
