#!/bin/bash
# Script to clean pycache files from your project

find /Users/mbaosint/Desktop/Projects/CreepyAI -name "__pycache__" -type d -exec rm -rf {} +  2>/dev/null || true
find /Users/mbaosint/Desktop/Projects/CreepyAI -name "*.pyc" -delete
find /Users/mbaosint/Desktop/Projects/CreepyAI -name "*.pyo" -delete
find /Users/mbaosint/Desktop/Projects/CreepyAI -name "*.pyd" -delete

echo "Python cache cleared successfully!"
