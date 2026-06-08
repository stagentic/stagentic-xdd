#!/usr/bin/env python3
# PostToolUse(Bash): after a pytest green on an in-flight source_paths file,
# inject a reminder to run focused mutmut before moving on. The observed miss
# is reaching green and continuing without the focused mutation check. This
# only fires when a mutmut source_paths file has uncommitted changes — i.e.
# a mutation target is being developed. PostToolUse cannot block; this is a
# reminder, and whether it alone changes behaviour is what we observe.
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib

project_dir = pathlib.Path(
    os.environ.get("CLAUDE_PROJECT_DIR")
    or pathlib.Path(__file__).resolve().parents[2]
)

data = json.load(sys.stdin)
command = (data.get("tool_input") or {}).get("command", "")
if "pytest" not in command:
    sys.exit(0)

response = json.dumps(data.get("tool_response", ""))
passed = re.search(r"\d+ passed", response) is not None
failed = (
    re.search(r"\d+ (failed|error)", response) is not None
    or "errors during collection" in response
    or "no tests ran" in response
)
if not (passed and not failed):
    sys.exit(0)

inflight = []
for pyproject in sorted(project_dir.glob("*/pyproject.toml")):
    try:
        conf = tomllib.loads(pyproject.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        continue
    source_paths = conf.get("tool", {}).get("mutmut", {}).get("source_paths", [])
    for rel in source_paths:
        repo_rel = (pyproject.parent / rel).relative_to(project_dir)
        status = subprocess.run(
            ["git", "-C", str(project_dir), "status", "--porcelain", "--", str(repo_rel)],
            capture_output=True,
            text=True,
        )
        if status.stdout.strip():
            inflight.append(str(repo_rel))

if not inflight:
    sys.exit(0)

context = (
    "Green reached with an in-flight mutation target uncommitted: "
    + ", ".join(inflight)
    + ". Per docs/working-practices.md, the green step starts with focused "
    "mutmut on that file (see COMMANDS.md) — run it now and dial back any "
    "survivor before continuing. Do not move on from this green without it."
)
print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": context,
            }
        }
    )
)
