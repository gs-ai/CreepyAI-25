#!/bin/bash

# CreepyAI Python Environment Upgrade Script
# This script upgrades the existing conda environment or creates a new one
# with Python 3.11 and installs all required dependencies

echo "CreepyAI Python Environment Upgrade"
echo "=================================="

# Check conda availability
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH."
    echo "Please install Anaconda or Miniconda and try again."
    exit 1
fi

# Specify Python 3.11 instead of latest version
PYTHON_VERSION="3.11"
echo "Using Python $PYTHON_VERSION for optimal compatibility"

# Set environment name - keep the existing name
DEFAULT_ENV_NAME="creepyai25ENV"
ENV_NAME=$DEFAULT_ENV_NAME

# Check if environment already exists
ENV_EXISTS=false
if conda info --envs | grep -q "$ENV_NAME"; then
    ENV_EXISTS=true
    echo "Found existing environment: $ENV_NAME"
    
    # Ask how to proceed with existing environment
    echo "How would you like to proceed?"
    echo "1) Create a backup and update the existing environment (recommended)"
    echo "2) Remove and recreate the environment"
    echo "3) Create a new environment with a different name"
    echo "4) Abort upgrade"
    
    read -p "Enter option (1-4): " option
    
    case $option in
        1)
            # Create backup of the environment
            BACKUP_NAME="${ENV_NAME}_backup_$(date +%Y%m%d%H%M%S)"
            echo "Creating backup of environment as: $BACKUP_NAME"
            conda create -y --name $BACKUP_NAME --clone $ENV_NAME
            echo "Backup created. Proceeding to update existing environment."
            ;;
        2)
            # Remove and recreate
            echo "Removing existing environment: $ENV_NAME"
            conda env remove -n $ENV_NAME
            ENV_EXISTS=false
            ;;
        3)
            # Create with new name
            read -p "Enter new environment name: " new_name
            if [ -n "$new_name" ]; then
                ENV_NAME=$new_name
                ENV_EXISTS=false
            else
                echo "Invalid name. Using default: $DEFAULT_ENV_NAME"
            fi
            ;;
        4)
            # Abort
            echo "Upgrade aborted."
            exit 0
            ;;
        *)
            echo "Invalid option. Aborting upgrade."
            exit 1
            ;;
    esac
fi

if [ "$ENV_EXISTS" = true ]; then
    # Update existing environment
    echo "Updating environment '$ENV_NAME' to Python $PYTHON_VERSION"
    
    # Activate the environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate $ENV_NAME
    
    # Update Python version
    echo "Updating Python version to $PYTHON_VERSION..."
    conda install -y python=$PYTHON_VERSION
else
    # Create new environment
    echo "Creating new environment '$ENV_NAME' with Python $PYTHON_VERSION..."
    conda create -y -n $ENV_NAME python=$PYTHON_VERSION
    
    # Activate the new environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate $ENV_NAME
fi

# Install core dependencies using pip
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install additional dependencies with conda
echo "Installing GUI dependencies with conda..."
conda install -y -c conda-forge pyqt=5.15
conda install -y -c conda-forge pyqtwebkit

echo ""
echo "Environment setup complete! To use the environment:"
echo "--------------------------------------------------------"
echo "  conda activate $ENV_NAME"
echo ""
echo "To make this environment the default for CreepyAI, add the following line"
echo "to your shell profile (~/.bashrc, ~/.zshrc, or similar):"
echo ""
echo "  export CREEPYAI_CONDA_ENV=\"$ENV_NAME\""
echo ""
echo "Then update your startup scripts to use this environment automatically."
echo "--------------------------------------------------------"
