#!/bin/bash

# Script to convert .ui files to Python files
# Usage: ./generate_ui.sh

UI_DIR="app/gui/ui"
UI_FILE="creepyai_mainwindow.ui"

if [ -f "$UI_DIR/$UI_FILE" ]; then
    echo "Generating Python UI file from $UI_DIR/$UI_FILE..."
    pyuic5 -o "$UI_DIR/creepyai_mainwindow_ui.py" "$UI_DIR/$UI_FILE"
    echo "UI file generated successfully."
else
    echo "Warning: UI file $UI_DIR/$UI_FILE not found."
    echo "Using placeholder UI file instead."
fi

# Make the script executable
chmod +x generate_ui.sh
