#!/bin/bash

# Simple script to properly push changes to GitHub
echo "Pushing changes to GitHub..."

# Add all changes
git add .

# Commit changes
echo "Enter a commit message (or press Enter for default):"
read -p "> " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update CreepyAI with Python 3.11 compatibility improvements"
fi
git commit -m "$COMMIT_MSG"

# Push to main branch
echo "Pushing to main branch..."
git push origin main

echo "Done!"
