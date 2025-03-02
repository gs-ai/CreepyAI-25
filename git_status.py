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
logger = logging.getLogger('CreepyAI-GitStatus')

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

def show_branch_status():
    """Show current branch status and recent commits."""
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

if __name__ == "__main__":
    show_branch_status()
