#!/bin/bash
# Simplified launcher for CreepyAI

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "${PROJECT_ROOT}"

# Add project directories to Python path
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Launch the application
if [ "$1" == "--tkinter" ]; then
    echo "Starting CreepyAI with Tkinter UI..."
    python launch_creepyai.py --ui tkinter "$@"
else
    echo "Starting CreepyAI..."
    python launch_creepyai.py "$@"
fi
