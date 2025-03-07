#!/bin/bash

# Compile resources for CreepyAI
# This script compiles QRC and UI files

echo "======================================"
echo "CreepyAI - Resource Compiler"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# Create placeholder icons if they don't exist
echo "Creating placeholder icons..."
python create_placeholder_icons.py

# Create necessary directories
echo "Creating directory structure..."
mkdir -p resources/templates
mkdir -p resources/data
mkdir -p gui/ui

# Compile QRC file
echo "Compiling Qt resources..."
if command -v pyrcc5 &> /dev/null; then
    pyrcc5 -o resources/creepy_resources_rc.py resources/creepy_resources.qrc
    if [ $? -eq 0 ]; then
        echo "✓ Qt resources compiled successfully"
    else
        echo "✗ Failed to compile Qt resources"
        exit 1
    fi
else
    echo "✗ pyrcc5 command not found. Is PyQt5 installed?"
    echo "Try running: pip install PyQt5"
    exit 1
fi

# Compile UI files
echo "Compiling UI files..."
python compile_ui.py
if [ $? -eq 0 ]; then
    echo "✓ UI files compiled successfully"
else
    echo "✗ Failed to compile UI files"
    exit 1
fi

echo "Resource compilation completed successfully"
