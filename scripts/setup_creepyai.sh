#!/bin/bash

# CreepyAI Setup Script
# This script sets up a clean environment for CreepyAI

echo "======================================"
echo "CreepyAI - Environment Setup"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Improved conda detection
CONDA_AVAILABLE=false

# Check if CONDA_PREFIX is set (user is already in a conda environment)
if [ -n "$CONDA_PREFIX" ]; then
    CONDA_AVAILABLE=true
    echo "Active conda environment detected: $CONDA_PREFIX"
    CONDA_CMD="$CONDA_PREFIX/bin/conda"
    # If we're in a conda environment but can't find the conda binary,
    # try to locate conda in the parent directory structure
    if [ ! -f "$CONDA_CMD" ]; then
        CONDA_BASE=$(echo "$CONDA_PREFIX" | sed -E 's|/envs/[^/]+||')
        CONDA_CMD="$CONDA_BASE/bin/conda"
    fi
# Check if conda command is available in PATH
elif command -v conda &> /dev/null; then
    CONDA_AVAILABLE=true
    echo "Conda detected in PATH"
    CONDA_CMD=$(which conda)
# Try common conda installation locations
else
    common_locations=(
        "$HOME/anaconda3/bin/conda"
        "$HOME/miniconda3/bin/conda"
        "/opt/anaconda3/bin/conda"
        "/usr/local/anaconda3/bin/conda"
    )
    
    for loc in "${common_locations[@]}"; do
        if [ -f "$loc" ]; then
            CONDA_AVAILABLE=true
            CONDA_CMD="$loc"
            echo "Conda found at: $CONDA_CMD"
            break
        fi
    done
fi

# Final conda availability check
if [ "$CONDA_AVAILABLE" = true ]; then
    if [ ! -f "$CONDA_CMD" ]; then
        echo "Warning: Conda detected but binary not found at: $CONDA_CMD"
        CONDA_AVAILABLE=false
    else
        echo "Using conda at: $CONDA_CMD"
    fi
else
    echo "Conda not found, will use virtualenv instead"
    # Check for virtualenv
    if ! command -v python3 -m venv &> /dev/null; then
        echo "Error: Neither conda nor python venv is available"
        echo "Please install either conda or python venv to continue"
        exit 1
    fi
fi

# Ask user for installation type
echo
echo "Select installation type:"
echo "1. Use conda environment (recommended)"
echo "2. Use Python virtualenv"
echo "3. Install in current environment (not recommended)"
echo "4. Skip environment setup (use current environment)"
read -p "Choice (1-4): " install_type
echo

case $install_type in
    1)
        if [ "$CONDA_AVAILABLE" = false ]; then
            echo "Error: Conda is not available but you selected conda installation"
            exit 1
        fi
        
        # Create conda environment
        echo "Creating conda environment from environment.yml..."
        "$CONDA_CMD" env create -f environment.yml
        
        # Activate the environment
        echo "To activate the environment, run:"
        echo "conda activate creepyai"
        echo
        echo "After activation, test CreepyAI by running:"
        echo "./launch_macos.sh"
        ;;
    2)
        # Create virtualenv
        echo "Creating Python virtual environment..."
        python3 -m venv venv
        
        # Activate the environment
        source venv/bin/activate
        
        # Install dependencies
        echo "Installing dependencies..."
        pip install -r requirements.txt
        
        echo "Virtual environment created and dependencies installed"
        echo "To activate the environment in the future, run:"
        echo "source venv/bin/activate"
        echo
        echo "Test CreepyAI by running:"
        echo "./launch_macos.sh"
        ;;
    3)
        # Install in current environment
        echo "Installing dependencies in current environment..."
        pip install -r requirements.txt
        
        echo "Dependencies installed in current environment"
        echo "Test CreepyAI by running:"
        echo "./launch_macos.sh"
        ;;
    4)
        echo "Skipping environment setup, using current environment..."
        echo "Make sure all required dependencies are installed."
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Make scripts executable
echo "Making scripts executable..."
chmod +x launch_macos.sh 2>/dev/null || true
chmod +x fix_pyqt_conda.sh 2>/dev/null || true
chmod +x resources/compile_resources.sh 2>/dev/null || true

# Set up resources
echo
echo "Setting up resources..."
python setup_resources.py

echo
echo "Setup completed!"
echo "If you encounter any issues with PyQt5, run:"
echo "./fix_pyqt_conda.sh"
