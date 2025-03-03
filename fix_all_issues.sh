#!/bin/bash

# Fix script for multiple CreepyAI issues
echo "Starting CreepyAI comprehensive fix..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the project directory
cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d "creepyai25ENV" ]; then
    echo "Activating virtual environment..."
    source creepyai25ENV/bin/activate
fi

# Fix 1: Plugin Dialog Fix
echo "Step 1: Fixing plugin dialog configuration issue..."
python3 creepy/ui/plugin_dialog_fix.py

# Fix 2: PersonProjectWizard Fix
echo "Step 2: Fixing PersonProjectWizard NoneType error..."
python3 creepy/ui/fix_wizard_plugin_error.py

# Fix 3: Project Loading Fix
echo "Step 3: Fixing project loading issue..."
python3 creepy/models/fix_project_loading.py

# Check results
echo ""
echo "======================================================"
echo "Fixes have been applied. Please restart CreepyAI with:"
echo "python /Users/mbaosint/Desktop/Projects/CreepyAI/CreepyMain.py"
echo ""
echo "If you encounter any issues:"
echo "1. Check the logs at ~/.creepyai/logs/"
echo "2. Restore backups (.bak files) if needed"
echo "3. Submit an error report with the log details"
echo "======================================================"

# Make the script executable
chmod +x "$SCRIPT_DIR/fix_all_issues.sh"
