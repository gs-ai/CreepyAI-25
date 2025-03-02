#!/bin/bash
# Simple script to install Python 3.11 in the current conda environment

echo "Installing Python 3.11 in current conda environment"
echo "=================================================="

# Get current environment name
CURRENT_ENV=$(conda info --envs | grep "*" | awk '{print $1}')

if [ -z "$CURRENT_ENV" ]; then
    echo "Error: Could not determine current conda environment."
    echo "Please make sure a conda environment is activated."
    exit 1
fi

echo "Current conda environment: $CURRENT_ENV"
echo "Installing Python 3.11..."

# Install Python 3.11
conda install -y python=3.11

# Check the installation
PYTHON_VERSION=$(python --version)

echo "Python version after installation: $PYTHON_VERSION"
echo ""
echo "You may need to reinstall your project dependencies:"
echo "pip install -r requirements.txt"

echo ""
echo "Done!"
