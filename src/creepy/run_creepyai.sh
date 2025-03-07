#!/bin/bash
# filepath: run_creepyai.sh
# Simplified launcher for CreepyAI

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Add project directories to Python path
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Launch the application
if [ "$1" == "--tkinter" ]; then
    echo "Starting CreepyAI with Tkinter UI..."
    python launch_creepyai.py --ui tkinter "$@"
else
    echo "Starting CreepyAI..."
    python launch_creepyai.py "$@"
fi
