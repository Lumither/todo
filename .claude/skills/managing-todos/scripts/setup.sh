#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"

if command -v todo &>/dev/null; then
    echo '{"ok": true, "message": "todo CLI already installed"}'
    exit 0
fi

if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    pip install -e "$PROJECT_ROOT" -q 2>/dev/null
    echo '{"ok": true, "message": "todo CLI installed from project root"}'
else
    echo '{"ok": false, "error": "Could not find project root. Install manually: pip install -e /path/to/todo"}'
    exit 1
fi
