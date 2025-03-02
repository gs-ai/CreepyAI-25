#!/bin/bash

# Script to update GitHub repository with all recent changes
# This will commit and push all the files we've created/modified

echo "CreepyAI GitHub Repository Update"
echo "================================="

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

# Check for remote repository
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
    echo "No remote repository found."
    read -p "Would you like to add a GitHub remote? (y/N): " ADD_REMOTE
    if [[ "$ADD_REMOTE" =~ ^[Yy]$ ]]; then
        read -p "Enter your GitHub repository URL: " GITHUB_URL
        git remote add origin "$GITHUB_URL"
        echo "Added remote origin: $GITHUB_URL"
    else
        echo "No remote added. Changes will only be committed locally."
    fi
else
    echo "Found remote repository: $REMOTE_URL"
fi

# Check for changes
if git diff-index --quiet HEAD --; then
    echo "No changes detected in tracked files."
else
    echo "Changes detected in tracked files."
fi

# Show untracked files
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo "Untracked files found:"
    echo "$UNTRACKED" | sed 's/^/  /'
fi

# Prompt for commit message
echo ""
echo "Enter a commit message for these changes:"
read -p "> " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update CreepyAI with Python 3.11 compatibility and improved requirements"
    echo "Using default commit message: $COMMIT_MSG"
fi

# Stage all files (including new ones)
echo "Staging all changes..."
git add .

# Commit changes
echo "Committing changes..."
git commit -m "$COMMIT_MSG"

# Show summary of changes
echo ""
echo "Commit summary:"
git show --stat HEAD

# Push to remote if available
if [ -n "$REMOTE_URL" ]; then
    echo ""
    read -p "Push changes to remote repository? (y/N): " PUSH_CHANGES
    
    if [[ "$PUSH_CHANGES" =~ ^[Yy]$ ]]; then
        # Check current branch
        CURRENT_BRANCH=$(git branch --show-current)
        echo "Pushing to $CURRENT_BRANCH branch..."
        
        # Try to push
        if git push origin "$CURRENT_BRANCH"; then
            echo "Successfully pushed to remote repository!"
        else
            echo "Failed to push to remote repository."
            echo "You might need to pull changes first or resolve conflicts."
            read -p "Try to pull before pushing? (y/N): " PULL_FIRST
            
            if [[ "$PULL_FIRST" =~ ^[Yy]$ ]]; then
                echo "Pulling latest changes..."
                git pull origin "$CURRENT_BRANCH"
                
                echo "Trying to push again..."
                if git push origin "$CURRENT_BRANCH"; then
                    echo "Successfully pushed to remote repository!"
                else
                    echo "Failed to push. Please resolve conflicts manually."
                fi
            fi
        fi
    else
        echo "Changes committed locally but not pushed to remote."
    fi
fi

echo ""
echo "Repository update complete!"
echo "----------------------------------------"
echo "Next steps:"
echo "1. Make sure all changes are correctly pushed to GitHub"
echo "2. Update any documentation or release notes as needed"
echo "3. Inform collaborators about the Python 3.11 requirement"
echo "----------------------------------------"
