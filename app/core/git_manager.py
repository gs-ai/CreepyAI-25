#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('CreepyAI-GitManager')

# Repository URL
REPO_URL = "https://github.com/gs-ai/CreepyAI-25"

def git_command(command):
    """Execute a git command and return the output."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            shell=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        return None

def format_time_ago(timestamp):
    """Format a timestamp as a human-readable time ago string."""
    try:
        commit_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %z")
        now = datetime.now().astimezone()
        delta = now - commit_time
        
        seconds = delta.total_seconds()
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours ago"
        else:
            return f"{int(seconds / 86400)} days ago"
    except Exception:
        return timestamp

def setup_repository():
    """Setup or verify the git repository configuration."""
    print("\n=== Setting Up Repository ===")
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        logger.info("Initializing git repository...")
        if git_command("git init") is None:
            return False
    
    # Check if remote origin is set up
    remotes = git_command("git remote -v")
    if remotes and "origin" in remotes:
        logger.info("Remote origin already configured")
        
        # Check if it's the correct URL
        if REPO_URL not in remotes:
            logger.info(f"Updating remote origin URL to {REPO_URL}")
            if git_command(f"git remote set-url origin {REPO_URL}") is None:
                return False
    else:
        # Add the remote origin
        logger.info(f"Adding remote origin: {REPO_URL}")
        if git_command(f"git remote add origin {REPO_URL}") is None:
            return False
    
    # Set Git identity if not configured
    user_name = git_command("git config --get user.name")
    user_email = git_command("git config --get user.email")
    
    if not user_name or not user_email:
        logger.info("Git identity not fully configured")
        if not user_name:
            name = input("Enter your Git username: ")
            if git_command(f'git config user.name "{name}"') is None:
                return False
        if not user_email:
            email = input("Enter your Git email: ")
            if git_command(f'git config user.email "{email}"') is None:
                return False
    
    logger.info("Repository setup completed successfully!")
    return True

def check_default_branch():
    """Check the default branch of the remote repository."""
    try:
        # Fetch the latest from remote
        git_command("git fetch")
        
        # Try to get info about the remote's HEAD
        remote_head = git_command("git symbolic-ref refs/remotes/origin/HEAD")
        if remote_head:
            # Extract the branch name (e.g., "refs/remotes/origin/main" -> "main")
            default_branch = remote_head.split("/")[-1]
            return default_branch
        
        # Alternative method if symbolic-ref doesn't work
        ls_remote = git_command("git ls-remote --symref origin HEAD")
        if ls_remote:
            lines = ls_remote.splitlines()
            for line in lines:
                if "refs/heads/" in line:
                    parts = line.split()
                    for part in parts:
                        if "refs/heads/" in part:
                            return part.split("/")[-1]
    except Exception as e:
        logger.error(f"Failed to determine default branch: {e}")
    
    # Default to "main" if we can't determine
    return "main"

def fix_branch():
    """Fix the branch name mismatch and push to the correct branch."""
    print("\n=== Fixing Branch Issues ===")
    if not os.path.exists('.git'):
        logger.error("Not a git repository. Initialize git first.")
        return False
    
    # Get current branch
    current_branch = git_command("git branch --show-current")
    if not current_branch:
        logger.error("Failed to get current branch.")
        return False
    
    # Determine remote default branch
    default_branch = check_default_branch()
    logger.info(f"Remote default branch appears to be: {default_branch}")
    
    if current_branch != default_branch:
        print(f"\nBranch mismatch detected: Local '{current_branch}' vs Remote '{default_branch}'")
        
        # Ask if the user wants to rename the branch
        choice = input(f"Rename local branch from '{current_branch}' to '{default_branch}'? (y/n): ")
        
        if choice.lower() in ['y', 'yes']:
            # Create new branch if it doesn't exist
            if not git_command(f"git show-ref --verify --quiet refs/heads/{default_branch}"):
                logger.info(f"Creating new branch '{default_branch}' from '{current_branch}'")
                if git_command(f"git branch {default_branch}") is None:
                    return False
            
            # Checkout the correct branch
            logger.info(f"Checking out branch '{default_branch}'")
            if git_command(f"git checkout {default_branch}") is None:
                return False
            
            # If we created a new branch, we need to push and set upstream
            logger.info("Pushing to correct branch and setting upstream")
            if git_command(f"git push -u origin {default_branch}") is None:
                # If push fails, try without -u
                if git_command(f"git push origin {default_branch}") is None:
                    return False
            
            # Ask if the user wants to delete the old branch
            delete_choice = input(f"Delete old branch '{current_branch}'? (y/n): ")
            if delete_choice.lower() in ['y', 'yes']:
                if git_command(f"git branch -D {current_branch}") is None:
                    logger.warning(f"Failed to delete branch '{current_branch}'")
            
            print(f"Successfully switched to '{default_branch}' branch and pushed to remote.")
        else:
            # If user doesn't want to rename, push to current branch but warn
            print(f"\nKeeping local branch as '{current_branch}'.")
            print(f"Warning: This will create a separate branch from the default '{default_branch}' on remote.")
            
            push_choice = input(f"Push '{current_branch}' to remote? (y/n): ")
            if push_choice.lower() in ['y', 'yes']:
                if git_command(f"git push -u origin {current_branch}") is None:
                    return False
                print(f"Pushed '{current_branch}' to remote.")
    else:
        # Branches match, just push
        logger.info(f"Local and remote branches match: '{current_branch}'")
        if git_command(f"git push origin {current_branch}") is None:
            return False
        print(f"Successfully pushed to '{current_branch}'.")
    
    return True

def show_status():
    """Show current branch status and recent commits."""
    print("\n=== Repository Status ===")
    if not os.path.exists('.git'):
        logger.error("Not a git repository. Initialize git first.")
        return False
    
    # Get current branch
    current_branch = git_command("git branch --show-current")
    if not current_branch:
        logger.error("Failed to get current branch.")
        return False
    
    print("\n=== Branch Status ===")
    print(f"Current branch: {current_branch}")
    
    # Check if branch is up to date with remote
    try:
        git_command("git fetch")
        ahead_behind = git_command(f"git rev-list --left-right --count origin/{current_branch}...{current_branch}")
        if ahead_behind:
            behind, ahead = ahead_behind.split()
            if int(ahead) > 0:
                print(f"Your branch is ahead of 'origin/{current_branch}' by {ahead} commit(s)")
            if int(behind) > 0:
                print(f"Your branch is behind 'origin/{current_branch}' by {behind} commit(s)")
            if int(ahead) == 0 and int(behind) == 0:
                print(f"Your branch is up to date with 'origin/{current_branch}'")
    except Exception:
        print("Unable to compare with remote branch. Remote may not be configured or branch doesn't exist remotely.")
    
    # Get recent commits
    print("\n=== Recent Commits ===")
    recent_commits = git_command('git log -n 5 --pretty=format:"%h|%an|%ad|%s" --date=format:"%Y-%m-%d %H:%M:%S %z"')
    if recent_commits:
        for commit in recent_commits.split('\n'):
            parts = commit.split('|')
            if len(parts) >= 4:
                hash_id, author, date, message = parts[0], parts[1], parts[2], parts[3]
                time_ago = format_time_ago(date)
                print(f"{hash_id} ({time_ago}) by {author}: {message}")
    
    # Check for uncommitted changes
    status = git_command("git status --porcelain")
    if status:
        print("\n=== Uncommitted Changes ===")
        modified = 0
        new = 0
        deleted = 0
        
        for line in status.split('\n'):
            if line.startswith(' M') or line.startswith('M '):
                modified += 1
            elif line.startswith('??'):
                new += 1
            elif line.startswith(' D') or line.startswith('D '):
                deleted += 1
        
        print(f"Modified files: {modified}")
        print(f"New files: {new}")
        print(f"Deleted files: {deleted}")
        print("\nUse 'git status' for details")
    else:
        print("\nWorking tree clean, no uncommitted changes.")
    
    return True

def push_updates():
    """Add all changes, commit them with a message, and push to remote."""
    print("\n=== Pushing Updates ===")
    # First ensure repository is set up
    if not setup_repository():
        logger.error("Failed to set up git repository")
        return False
    
    # Get current branch
    current_branch = git_command("git branch --show-current")
    if not current_branch:
        logger.error("Failed to get current branch.")
        return False
    
    # Determine remote default branch
    default_branch = check_default_branch()
    if current_branch != default_branch:
        logger.info(f"Current branch '{current_branch}' doesn't match default branch '{default_branch}'")
        switch_choice = input(f"Switch from '{current_branch}' to '{default_branch}'? (y/n): ")
        
        if switch_choice.lower() in ['y', 'yes']:
            # Check if the branch exists locally
            branches = git_command("git branch")
            if branches and default_branch in branches:
                # Branch exists, just checkout
                logger.info(f"Checking out existing branch '{default_branch}'")
                if git_command(f"git checkout {default_branch}") is None:
                    return False
            else:
                # Create and checkout the branch
                logger.info(f"Creating and checking out branch '{default_branch}'")
                if git_command(f"git checkout -b {default_branch}") is None:
                    return False
            
            # Update current_branch after switching
            current_branch = default_branch
        else:
            logger.info(f"Continuing with current branch '{current_branch}'")
    
    # Add all files
    logger.info("Adding all changed files...")
    if git_command("git add .") is None:
        return False
    
    # Check if there are changes to commit
    status = git_command("git status --porcelain")
    if not status:
        logger.info("No changes to commit.")
        return True
    
    # Get commit message
    commit_message = input("Enter commit message: ")
    if not commit_message:
        commit_message = "Update CreepyAI components"
    
    # Commit changes
    logger.info(f"Committing changes with message: '{commit_message}'")
    if git_command(f'git commit -m "{commit_message}"') is None:
        return False
    
    # Push changes
    logger.info(f"Pushing changes to remote repository on branch '{current_branch}'...")
    if git_command(f"git push -u origin {current_branch}") is None:
        logger.warning("Push failed. The remote branch might not exist.")
        return False
    
    logger.info("Updates pushed successfully!")
    return True

def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("CreepyAI Git Manager".center(50))
    print("=" * 50)
    print("1. Setup Repository")
    print("2. View Repository Status")
    print("3. Fix Branch Issues")
    print("4. Push Updates")
    print("5. Exit")
    print("=" * 50)

def main():
    """Main function to run the git manager."""
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            setup_repository()
        elif choice == '2':
            show_status()
        elif choice == '3':
            fix_branch()
        elif choice == '4':
            push_updates()
        elif choice == '5':
            print("Exiting Git Manager...")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Check if command line arguments were provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_repository()
        elif command == "status":
            show_status()
        elif command == "fix":
            fix_branch()
        elif command == "push":
            push_updates()
        elif command == "help":
            print("Usage: python git_manager.py [command]")
            print("Commands:")
            print("  setup  - Setup or verify repository configuration")
            print("  status - Show repository status and recent commits")
            print("  fix    - Fix branch naming issues")
            print("  push   - Commit and push changes")
            print("  help   - Show this help message")
            print("No command will start the interactive menu")
    else:
        main()
