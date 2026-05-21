"""TranscriptRenderer — render a Claude JSONL transcript line into markdown.

Vendored so the test-runner spike can run without depending on a sibling
agent-utils package. Only the rendering class is included here; the
live-streaming counterpart (with its asyncio/threading) is not used.
"""
import json
from datetime import datetime


class TranscriptRenderer:
    """JSONL line → markdown rendering. Pure: no I/O, no threading."""

    def __init__(self):
        self._last_tool = None

    def render_line(self, raw_line):
        entry = json.loads(raw_line)
        if entry.get("isMeta"):
            return ""
        timestamp = self._extract_time(entry.get("timestamp", ""))
        message = entry.get("message", {})
        content = message.get("content", [])
        parts = []

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(f"`{timestamp}`\n\n{item['text']}")
                    elif item.get("type") == "tool_use":
                        self._last_tool = item.get("name")
                        parts.append(self._render_tool_use(timestamp, item))
                    elif item.get("type") == "tool_result":
                        if self._last_tool not in ("Read", "Edit", "Skill"):
                            result_text = item.get("content", "")
                            if result_text:
                                parts.append(f"```\n{result_text}\n```")

        if not parts:
            return ""
        return "\n\n".join(parts) + "\n\n"

    def _extract_time(self, timestamp):
        if not timestamp:
            return ""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%H:%M:%SZ")
        except ValueError:
            return ""

    def _render_tool_use(self, timestamp, item):
        name = item.get("name", "unknown")
        tool_input = item.get("input", {})

        if name == "Edit":
            file_path = tool_input.get("file_path", "")
            old = tool_input.get("old_string", "")
            new = tool_input.get("new_string", "")
            return f"`{timestamp}` [TOOL] **Edit** `{file_path}`\n\nBefore:\n```\n{old}\n```\n\nAfter:\n```\n{new}\n```"

        if name == "Write":
            file_path = tool_input.get("file_path", "")
            file_content = tool_input.get("content", "")
            return f"`{timestamp}` [TOOL] **Write** `{file_path}`\n\n```\n{file_content}\n```"

        if name == "Read":
            key = tool_input.get("file_path", "")
        elif name == "Bash":
            key = tool_input.get("command", "")
        elif name == "Glob":
            key = tool_input.get("pattern", "")
        elif name == "Grep":
            key = tool_input.get("pattern", "")
        elif name == "Skill":
            key = tool_input.get("skill", "")
        else:
            key = str(tool_input)

        return f"`{timestamp}` [TOOL] **{name}** `{key}`"
