#!/bin/bash

# Script to create a feature branch and push changes for a pull request
# This works around the branch protection rules on the main branch

echo "CreepyAI Pull Request Workflow"
echo "============================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed or not in PATH."
    echo "Please install git and try again."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Error: Not in a git repository."
    echo "Please run this script from the root of your CreepyAI repository."
    exit 1
fi

# Create a new branch name with current date
DEFAULT_BRANCH="python311-compatibility-$(date +%Y%m%d)"
echo "Enter branch name (default: $DEFAULT_BRANCH):"
read -p "> " BRANCH_NAME
if [ -z "$BRANCH_NAME" ]; then
    BRANCH_NAME=$DEFAULT_BRANCH
fi

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    echo "Branch '$BRANCH_NAME' already exists."
    read -p "Do you want to use it anyway? (y/N): " USE_EXISTING
    if [[ ! "$USE_EXISTING" =~ ^[Yy]$ ]]; then
        echo "Please run the script again with a different branch name."
        exit 1
    fi
    
    # Checkout existing branch
    git checkout $BRANCH_NAME
else
    # Create and checkout a new branch
    echo "Creating new branch: $BRANCH_NAME"
    git checkout -b $BRANCH_NAME
fi

# Show status
git status

# Ask for confirmation before adding files
read -p "Add all changes to this branch? (y/N): " ADD_CHANGES
if [[ ! "$ADD_CHANGES" =~ ^[Yy]$ ]]; then
    echo "No changes added. You can add specific files with 'git add <file>'."
    exit 0
fi

# Add all files
git add .

# Commit changes
echo "Enter a commit message (or press Enter for default):"
read -p "> " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update CreepyAI with Python 3.11 compatibility improvements"
fi
git commit -m "$COMMIT_MSG"

# Push to remote
echo "Pushing branch to remote..."
git push -u origin $BRANCH_NAME

# Get the repository URL
REPO_URL=$(git remote get-url origin)
PR_URL=""

# Transform SSH URLs to HTTPS URLs for PR creation
if [[ $REPO_URL == *"git@github.com"* ]]; then
    # Convert SSH URL to HTTPS URL format
    PR_URL=$(echo $REPO_URL | sed -E 's|git@github.com:|https://github.com/|' | sed 's|.git$||')
elif [[ $REPO_URL == *"https://github.com"* ]]; then
    # Already in HTTPS format
    PR_URL=$(echo $REPO_URL | sed 's|.git$||')
fi

if [ -n "$PR_URL" ]; then
    echo ""
    echo "Branch pushed successfully!"
    echo ""
    echo "To create a pull request, go to:"
    echo "$PR_URL/pull/new/$BRANCH_NAME"
    echo ""
    echo "Or visit the repository on GitHub and you should see a prompt to create a pull request."
else
    echo ""
    echo "Branch pushed successfully!"
    echo "Please visit the repository on GitHub to create a pull request."
fi

echo "Done!"
