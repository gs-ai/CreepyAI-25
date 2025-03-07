#!/bin/bash

# Simple script to launch CreepyAI with Tkinter UI
echo "Launching CreepyAI with Tkinter UI..."

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Run the launcher with tkinter UI
python launch_creepyai.py --ui tkinter
