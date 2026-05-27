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
    kind = item.get("type")
    if kind == "text":
        return f"`{timestamp}`\n\n{item['text']}\n\n"
    if kind == "thinking":
        return f"`{timestamp}` [THINKING]\n\n"
    if kind == "tool_use":
        name = item.get("name", "")
        key = _tool_key(name, item.get("input", {}))
        return f"`{timestamp}` [TOOL] **{name}** `{key}`\n\n"
    if kind == "tool_result":
        result_content = item.get("content", "")
        if result_content:
            return f"```\n{result_content}\n```\n\n"
    return ""


def _render_entry(entry, timestamp):
    kind = entry.get("type")
    if kind == "ai-title":
        return f"`{timestamp}` [TITLE] {entry.get('aiTitle', '')}\n\n"
    if kind == "queue-operation":
        op = entry.get("operation", "")
        return f"`{timestamp}` [QUEUE] {op}\n\n"
    if kind == "last-prompt":
        return f"`{timestamp}` [LAST-PROMPT]\n\n"
    return ""


def _tool_key(name, tool_input):
    key_fields = {"Bash": "command", "Read": "file_path", "Write": "file_path",
                  "Edit": "file_path", "Glob": "pattern", "Grep": "pattern"}
    field = key_fields.get(name)
    if field:
        return tool_input.get(field, "")
    return str(tool_input)


def _format_time(timestamp):
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%SZ")
    except ValueError:
        return ""
