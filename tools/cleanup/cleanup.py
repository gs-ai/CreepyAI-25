#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup utility for CreepyAI project.
Helps organize files, remove backup files, and fix permissions.
"""

import os
import sys
import shutil
import argparse
import re
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CreepyAI Project Cleanup Utility")
    parser.add_argument("--project-dir", "-p", default=os.getcwd(),
                        help="Project directory (default: current working directory)")
    parser.add_argument("--remove-backups", "-b", action="store_true", 
                        help="Remove backup files (*.bak, *_backup, etc.)")
    parser.add_argument("--fix-permissions", "-f", action="store_true",
                        help="Fix file permissions (make Python files executable)")
    parser.add_argument("--clean-cache", "-c", action="store_true",
                        help="Clean Python cache files (__pycache__, *.pyc)")
    parser.add_argument("--organize", "-o", action="store_true",
                        help="Organize misplaced files")
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="Dry run (don't actually modify files)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    
    return parser.parse_args()

def remove_backup_files(project_dir, dry_run=False):
    """Remove backup files from the project."""
    backup_patterns = [
        r'.*\.bak$',
        r'.*\.backup$',
        r'.*\.old$',
        r'.*_backup$',
        r'.*\.py\.import_backup$',
        r'.*\.conflict.*$',
        r'.*\.swp$',
        r'.*~$'
    ]
    
    backup_files = []
    
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            for pattern in backup_patterns:
                if re.match(pattern, file):
                    backup_files.append(os.path.join(root, file))
                    break
    
    if not backup_files:
        logger.info("No backup files found")
        return 0
    
    logger.info(f"Found {len(backup_files)} backup files to remove")
    
    if dry_run:
        for file in backup_files:
            logger.info(f"Would remove: {file}")
        return len(backup_files)
    
    for file in backup_files:
        try:
            os.remove(file)
            logger.info(f"Removed: {file}")
        except Exception as e:
            logger.error(f"Failed to remove {file}: {str(e)}")
    
    return len(backup_files)

def clean_cache_files(project_dir, dry_run=False):
    """Clean Python cache files."""
    cache_dirs = []
    cache_files = []
    
    for root, dirs, files in os.walk(project_dir):
        # Find __pycache__ directories
        for d in dirs:
            if d == "__pycache__":
                cache_dirs.append(os.path.join(root, d))
        
        # Find .pyc files
        for file in files:
            if file.endswith(".pyc") or file.endswith(".pyo"):
                cache_files.append(os.path.join(root, file))
    
    total_cleaned = 0
    
    if cache_dirs:
        logger.info(f"Found {len(cache_dirs)} __pycache__ directories to remove")
        if not dry_run:
            for d in cache_dirs:
                try:
                    shutil.rmtree(d)
                    logger.info(f"Removed: {d}")
                    total_cleaned += 1
                except Exception as e:
                    logger.error(f"Failed to remove {d}: {str(e)}")
        else:
            for d in cache_dirs:
                logger.info(f"Would remove: {d}")
                total_cleaned += 1
    
    if cache_files:
        logger.info(f"Found {len(cache_files)} .pyc/.pyo files to remove")
        if not dry_run:
            for file in cache_files:
                try:
                    os.remove(file)
                    logger.info(f"Removed: {file}")
                    total_cleaned += 1
                except Exception as e:
                    logger.error(f"Failed to remove {file}: {str(e)}")
        else:
            for file in cache_files:
                logger.info(f"Would remove: {file}")
                total_cleaned += 1
    
    if not cache_dirs and not cache_files:
        logger.info("No cache files found")
    
    return total_cleaned

def fix_file_permissions(project_dir, dry_run=False):
    """Fix file permissions (make Python files executable)."""
    python_files = []
    
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        logger.info("No Python files found")
        return 0
    
    logger.info(f"Found {len(python_files)} Python files to fix permissions")
    
    if dry_run:
        for file in python_files:
            logger.info(f"Would fix permissions for: {file}")
        return len(python_files)
    
    for file in python_files:
        try:
            # Read first line to check for shebang
            with open(file, 'r', errors='ignore') as f:
                first_line = f.readline().strip()
            
            # Add execute permission (0o755 = rwxr-xr-x)
            if first_line.startswith("#!") or 'main' in file.lower():
                os.chmod(file, 0o755)
                logger.info(f"Fixed permissions for executable: {file}")
            else:
                # Regular Python files (0o644 = rw-r--r--)
                os.chmod(file, 0o644)
                logger.info(f"Fixed permissions for: {file}")
        except Exception as e:
            logger.error(f"Failed to fix permissions for {file}: {str(e)}")
    
    return len(python_files)

def organize_files(project_dir, dry_run=False):
    """Organize misplaced files."""
    # Define file types and their target directories
    file_types = {
        'models': ['.py'],
        'ui': ['.ui', '.py'],
        'resources': ['.png', '.jpg', '.svg', '.qrc'],
        'include': ['.html', '.js', '.css'],
        'plugins': ['.yapsy-plugin'],
        'docs': ['.md', '.txt', '.pdf'],
    }
    
    # Files that need to be moved
    files_to_move = {}
    
    # Scan for misplaced files
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            # Skip if already in the right place
            if any(d in root for d in file_types.keys()):
                continue
            
            # Check if file belongs to a specific directory
            for target_dir, extensions in file_types.items():
                if ext in extensions:
                    # Make sure target directory exists
                    target_path = os.path.join(project_dir, target_dir)
                    os.makedirs(target_path, exist_ok=True)
                    
                    # Check if file contains indicators for specific directories
                    if 'model' in file.lower() or 'entity' in file.lower():
                        target_path = os.path.join(project_dir, 'models')
                    elif 'ui' in file.lower() or 'dialog' in file.lower() or 'window' in file.lower():
                        target_path = os.path.join(project_dir, 'ui')
                    
                    # Destination path for the file
                    dest_path = os.path.join(target_path, file)
                    
                    # Don't overwrite existing files
                    if os.path.exists(dest_path):
                        logger.warning(f"Cannot move {file} to {target_path}: File already exists")
                        continue
                    
                    files_to_move[file_path] = dest_path
                    break
    
    if not files_to_move:
        logger.info("No files need to be organized")
        return 0
    
    logger.info(f"Found {len(files_to_move)} files to organize")
    
    if dry_run:
        for src, dest in files_to_move.items():
            logger.info(f"Would move: {src} -> {dest}")
        return len(files_to_move)
    
    moved_count = 0
    for src, dest in files_to_move.items():
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            # Move the file
            shutil.move(src, dest)
            logger.info(f"Moved: {src} -> {dest}")
            moved_count += 1
        except Exception as e:
            logger.error(f"Failed to move {src}: {str(e)}")
    
    return moved_count

def main():
    """Main function."""
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Starting cleanup in {args.project_dir}")
    
    if not os.path.isdir(args.project_dir):
        logger.error(f"{args.project_dir} is not a directory")
        return 1
    
    total_changes = 0
    
    if args.remove_backups:
        count = remove_backup_files(args.project_dir, args.dry_run)
        total_changes += count
    
    if args.clean_cache:
        count = clean_cache_files(args.project_dir, args.dry_run)
        total_changes += count
    
    if args.fix_permissions:
        count = fix_file_permissions(args.project_dir, args.dry_run)
        total_changes += count
    
    if args.organize:
        count = organize_files(args.project_dir, args.dry_run)
        total_changes += count
    
    if args.dry_run:
        logger.info(f"Dry run completed. {total_changes} changes would be made.")
    else:
        logger.info(f"Cleanup completed. Made {total_changes} changes.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
