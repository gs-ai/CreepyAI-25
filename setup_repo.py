#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('CreepyAI-RepoSetup')

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

def setup_repository():
    """Setup or verify the git repository configuration."""
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

if __name__ == "__main__":
    result = setup_repository()
    sys.exit(0 if result else 1)
