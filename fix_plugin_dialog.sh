#!/bin/bash

# Fix script for the PluginsConfigDialog missing config_manager argument error
echo "Starting CreepyAI plugin dialog fix..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the project directory
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d "creepyai25ENV" ]; then
    echo "Activating virtual environment..."
    source creepyai25ENV/bin/activate
fi

# Run the fix script
echo "Running plugin dialog fix script..."
python3 creepy/ui/plugin_dialog_fix.py

# Check the result
if [ $? -eq 0 ]; then
    echo "Fix applied successfully. Please restart CreepyAI."
else
    echo "Fix application failed. Please check the logs."
fi

# Provide instructions
echo ""
echo "======================================================"
echo "If the fix was successful, please restart CreepyAI with:"
echo "python /Users/mbaosint/Desktop/Projects/CreepyAI/CreepyMain.py"
echo "======================================================"
