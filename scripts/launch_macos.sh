#!/bin/bash

# CreepyAI macOS Launcher
# This script helps avoid Qt library conflicts on macOS

echo "======================================"
echo "CreepyAI - macOS Launcher"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Detect virtual environment
if [[ -d "venv" ]]; then
    source venv/bin/activate
    PYTHON_PATH="venv/bin/python"
elif [[ -n "$CONDA_PREFIX" ]]; then
    PYTHON_PATH="python"
    echo "Using active Conda environment: $CONDA_PREFIX"
else
    PYTHON_PATH="python"
    echo "No virtual environment detected, using system Python"
fi

# Clear any conflicting Qt plugin paths
unset QT_PLUGIN_PATH
unset DYLD_LIBRARY_PATH
unset DYLD_FRAMEWORK_PATH

# Get the path to the PyQt5 installation
QT_PATH=$($PYTHON_PATH -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__))")

if [ -n "$QT_PATH" ]; then
    echo "Found PyQt5 at: $QT_PATH"
    
    # Set Qt plugin path to the one from the Python environment
    export QT_PLUGIN_PATH="$QT_PATH/Qt5/plugins"
    
    # On macOS, also set QT_QPA_PLATFORM_PLUGIN_PATH
    export QT_QPA_PLATFORM_PLUGIN_PATH="$QT_PLUGIN_PATH/platforms"
    
    echo "Set QT_PLUGIN_PATH to: $QT_PLUGIN_PATH"
    echo "Set QT_QPA_PLATFORM_PLUGIN_PATH to: $QT_QPA_PLATFORM_PLUGIN_PATH"
else
    echo "Error: Could not find PyQt5 installation"
    exit 1
fi

# Launch CreepyAI
echo "Launching CreepyAI..."
$PYTHON_PATH launch_creepyai.py "$@"
