#!/bin/bash
# Script to install CreepyAI dependencies using conda

# Make sure we're in the right environment
echo "Installing dependencies for CreepyAI..."

# Install PyQt5 using conda (more reliable than pip for this package)
conda install -y -c conda-forge pyqt=5.15

# Install other dependencies using pip
pip install yapsy configobj Pillow

# Try to install PyQtWebKit
pip install --no-deps PyQt5-WebKit

echo "Installation complete. If PyQt5-WebKit failed, try: conda install -c conda-forge pyqtwebkit"
