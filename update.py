#!/usr/bin/env python3
"""
CreepyAI Update Script
----------------------
This script performs a forced update of the CreepyAI application.
It pulls the latest changes from the repository and updates any dependencies.
"""

import os
import sys
import subprocess
import shutil
import tempfile
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='creepyai_update.log'
)
logger = logging.getLogger('CreepyAI Update')

def check_git_installed():
    """Check if git is installed on the system"""
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def backup_current_installation(app_dir):
    """Create a backup of the current installation"""
    backup_dir = os.path.join(tempfile.gettempdir(), f"creepyai_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    logger.info(f"Backing up current installation to {backup_dir}")
    
    try:
        # Copy current installation to backup directory
        shutil.copytree(app_dir, backup_dir, ignore=shutil.ignore_patterns(
            '*.pyc', '__pycache__', '.git', '.gitignore', 'venv', 'env'
        ))
        print(f"Created backup at: {backup_dir}")
        return backup_dir
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        print(f"Error creating backup: {e}")
        return None

def update_from_git(app_dir, branch="main", repo_url=None):
    """Update CreepyAI from git repository"""
    current_dir = os.getcwd()
    
    try:
        # Change to app directory
        os.chdir(app_dir)
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(app_dir, ".git")):
            if repo_url:
                # Clone the repository if URL is provided
                print(f"No git repository found. Cloning from {repo_url}...")
                subprocess.run(["git", "clone", repo_url, "."], check=True)
            else:
                print("Not a git repository and no repository URL provided.")
                return False
        
        # Fetch latest changes
        print("Fetching latest changes...")
        subprocess.run(["git", "fetch", "--all"], check=True)
        
        # Backup local changes if any
        changes = subprocess.run(
            ["git", "status", "--porcelain"], 
            check=True, 
            stdout=subprocess.PIPE,
            text=True
        ).stdout.strip()
        
        if changes:
            print("Local changes detected. Stashing changes...")
            subprocess.run(["git", "stash"], check=True)
        
        # Reset to the latest version in the specified branch
        print(f"Updating to latest version from {branch} branch...")
        subprocess.run(["git", "reset", "--hard", f"origin/{branch}"], check=True)
        
        # Update submodules if any
        print("Updating submodules...")
        subprocess.run(["git", "submodule", "update", "--init", "--recursive"], check=True)
        
        print("Git update completed successfully.")
        return True
    
    except subprocess.SubprocessError as e:
        logger.error(f"Git update failed: {e}")
        print(f"Error during git update: {e}")
        return False
    
    finally:
        # Return to original directory
        os.chdir(current_dir)

def update_dependencies():
    """Update Python dependencies"""
    try:
        requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        
        if os.path.exists(requirements_file):
            print("Updating dependencies...")
            
            # Get Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            print(f"Using Python {python_version}")
            
            # First try to upgrade pip itself
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
                print("Pip has been updated to the latest version.")
            except subprocess.SubprocessError as e:
                logger.warning(f"Could not upgrade pip: {e}")
                print("Warning: Could not upgrade pip, continuing with existing version.")
            
            # Install dependencies with better error handling
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "--upgrade", "-r", requirements_file
                ], check=True)
                print("Dependencies updated successfully.")
                return True
            except subprocess.SubprocessError as e:
                logger.error(f"Dependency update failed: {e}")
                print(f"Error updating dependencies: {e}")
                
                # Offer to skip problematic dependencies
                response = input("Would you like to continue with the update process anyway? (y/N): ")
                if response.lower() == 'y':
                    print("Continuing update process despite dependency errors.")
                    return True
                return False
        else:
            print("Requirements file not found. Skipping dependency update.")
            return True
    
    except Exception as e:
        logger.error(f"Dependency update process failed: {e}")
        print(f"Unexpected error during dependency update: {e}")
        return False

def main():
    """Main update function"""
    parser = argparse.ArgumentParser(description="Force an update of the CreepyAI application")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup")
    parser.add_argument("--branch", default="main", help="Git branch to update from")
    parser.add_argument("--repo", help="Git repository URL to use if needed")
    parser.add_argument("--skip-deps", action="store_true", help="Skip updating dependencies")
    args = parser.parse_args()
    
    print("CreepyAI Update Tool")
    print("===================")
    
    # Current directory is assumed to be the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Application directory: {app_dir}")
    
    # Check if git is installed
    if not check_git_installed():
        print("Error: Git is not installed or not in PATH. Please install Git and try again.")
        return 1
    
    # Create backup if needed
    if not args.no_backup:
        backup_dir = backup_current_installation(app_dir)
        if not backup_dir:
            response = input("Backup failed. Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Update cancelled.")
                return 1
    
    # Update from git repository
    git_success = update_from_git(app_dir, args.branch, args.repo)
    
    # Update dependencies if requested
    deps_success = True
    if not args.skip_deps:
        deps_success = update_dependencies()
    
    # Final status message
    if git_success and deps_success:
        print("\nUpdate completed successfully!")
        print("You may need to restart CreepyAI for changes to take effect.")
        return 0
    else:
        print("\nUpdate completed with errors. Check the log file for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
