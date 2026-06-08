#!/usr/bin/env bash
# SessionStart hook: inject docs/working-practices.md verbatim into context.
# A CLAUDE.md pointer is advisory; injecting the literal text removes the
# read-but-not-applied / applied-as-paraphrase failure mode.
set -euo pipefail

project_dir="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
practices_file="$project_dir/docs/working-practices.md"

python3 - "$practices_file" <<'PY'
import json
import pathlib
import sys

practices = pathlib.Path(sys.argv[1])
preamble = (
    "Below is the project's working practices, injected verbatim from "
    "docs/working-practices.md. Apply it literally — do not rely on a "
    "paraphrase or a remembered summary.\n\n"
)
context = preamble + practices.read_text()
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}))
PY
