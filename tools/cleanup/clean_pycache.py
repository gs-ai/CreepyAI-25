#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script to clean __pycache__ directories and *.pyc files from the project.
Run this script to clean up Python cache files that can clutter your project.
"""

import os
import shutil
from pathlib import Path
import argparse

def find_pycache_directories(root_dir):
    """Find all __pycache__ directories in the given root directory."""
    pycache_dirs = []
    pyc_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Find __pycache__ directories
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
        
        # Find .pyc files outside __pycache__ directories
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                pyc_files.append(os.path.join(root, file))
    
    return pycache_dirs, pyc_files

def clean_pycache(root_dir, dry_run=False):
    """Remove __pycache__ directories and .pyc files."""
    pycache_dirs, pyc_files = find_pycache_directories(root_dir)
    
    if not pycache_dirs and not pyc_files:
        print("No __pycache__ directories or .pyc files found.")
        return
    
    # Handle __pycache__ directories
    for directory in pycache_dirs:
        if dry_run:
            print(f"Would remove directory: {directory}")
        else:
            print(f"Removing directory: {directory}")
            try:
                shutil.rmtree(directory)
            except Exception as e:
                print(f"Error removing {directory}: {e}")
    
    # Handle .pyc files
    for file in pyc_files:
        if dry_run:
            print(f"Would remove file: {file}")
        else:
            print(f"Removing file: {file}")
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error removing {file}: {e}")
    
    # Summary
    if dry_run:
        print(f"\nFound {len(pycache_dirs)} __pycache__ directories and {len(pyc_files)} .pyc/.pyo files.")
        print("No files were removed (dry run).")
    else:
        print(f"\nRemoved {len(pycache_dirs)} __pycache__ directories and {len(pyc_files)} .pyc/.pyo files.")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Clean __pycache__ directories and .pyc files from a Python project."
    )
    parser.add_argument(
        "-d", "--directory", 
        default=str(Path(__file__).parent.parent),
        help="Root directory to clean (default: project root)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be removed without actually removing anything"
    )
    
    args = parser.parse_args()
    
    print(f"Cleaning Python cache files in: {args.directory}")
    if args.dry_run:
        print("Dry run mode enabled - no files will be deleted.")
        
    clean_pycache(args.directory, args.dry_run)

if __name__ == "__main__":
    main()
