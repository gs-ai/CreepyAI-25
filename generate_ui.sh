#!/bin/bash

# Small wrapper around ``regenerate_ui.py`` to retain shell convenience.

set -euo pipefail

UI_DIR="app/gui/ui"
UI_FILE="creepyai_mainwindow.ui"
OUTPUT_FILE="creepyai_mainwindow_ui.py"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

PYTHON=${PYTHON:-python3}

if [[ ! -f "$PROJECT_ROOT/$UI_DIR/$UI_FILE" ]]; then
  echo "Error: UI file $UI_DIR/$UI_FILE not found." >&2
  exit 1
fi

PYUIC_BIN=${PYUIC_BIN:-pyuic5}

echo "Generating $OUTPUT_FILE from $UI_FILE using $PYTHON"
"$PYTHON" "$PROJECT_ROOT/regenerate_ui.py" --input "$PROJECT_ROOT/$UI_DIR/$UI_FILE" \
  --output "$PROJECT_ROOT/$UI_DIR/$OUTPUT_FILE" --pyuic "$PYUIC_BIN"
echo "UI generation complete."
