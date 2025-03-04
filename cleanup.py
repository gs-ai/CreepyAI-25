#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def remove_file(filepath):
    """Remove a file if it exists."""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"Removed: {filepath}")
            return True
        except Exception as e:
            print(f"Error removing {filepath}: {e}")
            return False
    else:
        print(f"File not found: {filepath}")
        return False

def cleanup_redundant_files():
    """Remove files that have been consolidated into git_manager.py"""
    
    # List of files to remove
    files_to_remove = [
        "push_updates.py",
        "setup_repo.py",
        "fix_branch.py",
        "git_status.py"
    ]
    
    # Get the base directory
    base_dir = os.getcwd()
    
    print("\nRemoving redundant Git management files...")
    
    # Remove each file
    for filename in files_to_remove:
        filepath = os.path.join(base_dir, filename)
        remove_file(filepath)
    
    print("\nCleanup complete!")
    print("All Git management functionality is now in 'git_manager.py'")
    print("You can use: python git_manager.py help")

if __name__ == "__main__":
    cleanup_redundant_files()
