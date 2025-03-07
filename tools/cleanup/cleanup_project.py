#!/usr/bin/env python3
"""
Cleanup Script for CreepyAI Project

This script removes unnecessary files, backup files, and redundant scripts
to clean up the project structure.
"""
import os
import shutil
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='cleanup.log'
)
logger = logging.getLogger('Cleanup')

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Files to keep (only these installation/fix scripts will be preserved)
KEEP_FILES = [
    'launch_creepyai.py',
    'run_creepyai.sh',
    'tools/debug_environment.py',
    'requirements.txt'
]

def remove_backup_files():
    """Remove all backup files in the project"""
    backup_patterns = [
        r'.*\.bak$',
        r'.*\.backup$',
        r'.*\.conflict_backup$',
        r'.*\.syntax_backup$',
        r'.*\.manual_backup$',
        r'.*\.extreme_backup$',
        r'.*\.extreme_new$',
        r'.*\.indent\.bak$',
        r'.*\.original$',
        r'.*\.temp\d*$'
    ]
    
    removed_count = 0
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            
            # Skip files in .git directory
            if '.git' in filepath:
                continue
                
            # Check if file matches any backup pattern
            for pattern in backup_patterns:
                if re.match(pattern, file):
                    print(f"Removing backup file: {rel_path}")
                    try:
                        os.remove(filepath)
                        removed_count += 1
                    except Exception as e:
                        print(f"Error removing {rel_path}: {e}")
                    break
    
    print(f"\nRemoved {removed_count} backup files")
    return removed_count

def remove_installation_scripts():
    """Remove redundant installation and fix scripts"""
    # Patterns to identify fix and installation scripts
    fix_patterns = [
        r'fix_.*\.py$',
        r'fix_.*\.sh$',
        r'install_.*\.py$',
        r'install_.*\.sh$',
        r'reinstall_.*\.sh$',
        r'run_.*fix.*\.sh$',
        r'run_with.*\.sh$'
    ]
    
    # List of specific scripts to remove
    specific_scripts = [
        'run_fixed.sh',
        'run_fixed_paths.sh',
        'run_syntax_fixed.sh',
        'run_with_fix.sh',
        'run_with_import_fixes.sh',
        'run_with_thorough_fix.sh',
        'reinstall_macos.sh',
        'tools/reinstall_all.sh',
        'tools/fix_python_path.py',
        'tools/fix_imports.py',
        'tools/fix_git_conflicts.py',
        'tools/fix_creepy_ui.py',
        'tools/fix_locations_list.py',
        'tools/fix_locations_list_syntax.py'
    ]
    
    removed_count = 0
    
    # Remove specific scripts
    for script in specific_scripts:
        filepath = os.path.join(PROJECT_ROOT, script)
        if os.path.exists(filepath):
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            
            # Check if this is a file we want to keep
            if any(rel_path == keep_file for keep_file in KEEP_FILES):
                print(f"Keeping essential file: {rel_path}")
                continue
                
            print(f"Removing installation script: {rel_path}")
            try:
                os.remove(filepath)
                removed_count += 1
            except Exception as e:
                print(f"Error removing {rel_path}: {e}")
    
    # Find and remove other fix/install scripts
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)
            
            # Skip files in .git directory or files we explicitly want to keep
            if '.git' in filepath or any(rel_path == keep_file for keep_file in KEEP_FILES):
                continue
                
            # Check if file matches any fix/install pattern
            for pattern in fix_patterns:
                if re.match(pattern, file):
                    print(f"Removing fix/install script: {rel_path}")
                    try:
                        os.remove(filepath)
                        removed_count += 1
                    except Exception as e:
                        print(f"Error removing {rel_path}: {e}")
                    break
    
    print(f"\nRemoved {removed_count} installation/fix scripts")
    return removed_count

def remove_log_files():
    """Remove log files"""
    log_patterns = [
        r'.*\.log$',
        r'.*_log$'
    ]
    
    removed_count = 0
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if any(re.match(pattern, file) for pattern in log_patterns):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, PROJECT_ROOT)
                print(f"Removing log file: {rel_path}")
                try:
                    os.remove(filepath)
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {rel_path}: {e}")
    
    print(f"\nRemoved {removed_count} log files")
    return removed_count

def clean_creepy_directory():
    """Clean the creepy directory and its contents"""
    creepy_dir = os.path.join(PROJECT_ROOT, 'creepy')
    if os.path.exists(creepy_dir):
        import_fixer = os.path.join(creepy_dir, 'import_fixer.py')
        
        # Remove the import fixer script if it exists
        if os.path.exists(import_fixer):
            print(f"Removing import fixer: {os.path.relpath(import_fixer, PROJECT_ROOT)}")
            try:
                os.remove(import_fixer)
            except Exception as e:
                print(f"Error removing import fixer: {e}")
        
        # Remove symbolic links in creepy directory
        for item in os.listdir(creepy_dir):
            item_path = os.path.join(creepy_dir, item)
            if os.path.islink(item_path):
                print(f"Removing symbolic link: creepy/{item}")
                try:
                    os.unlink(item_path)
                except Exception as e:
                    print(f"Error removing symbolic link: {e}")
    
    print("\nCleaned creepy directory")

def create_simplified_launcher():
    """Create a simplified launcher script"""
    launcher_path = os.path.join(PROJECT_ROOT, 'run_creepyai.sh')
    
    content = """#!/bin/bash
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
"""
    
    with open(launcher_path, 'w') as f:
        f.write(content)
    
    # Make the script executable
    os.chmod(launcher_path, 0o755)
    
    print(f"Created simplified launcher: run_creepyai.sh")

def main():
    """Main cleanup function"""
    print("CreepyAI Project Cleanup Tool")
    print("=============================")
    print("This will remove unnecessary backup files, installation scripts, and logs.")
    print("WARNING: This action cannot be undone!")
    
    confirm = input("Do you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Cleanup cancelled")
        return
    
    print("\nCleaning project...\n")
    
    # Remove backup files
    remove_backup_files()
    
    # Remove installation scripts
    remove_installation_scripts()
    
    # Remove log files
    remove_log_files()
    
    # Clean creepy directory
    clean_creepy_directory()
    
    # Create simplified launcher
    create_simplified_launcher()
    
    print("\nCleanup complete!")
    print("You can now use the simplified run_creepyai.sh script to launch the application.")

if __name__ == "__main__":
    main()
