#!/bin/bash

# Create and activate conda environment
conda create -n creepyai25ENV python=3.8 -y
conda activate creepyai25ENV

# Install PyQt5 with WebKit support
conda install -c conda-forge pyqt=5.15 -y
conda install -c conda-forge pyqtwebkit -y

# Install other required packages
pip install -r requirements.txt

echo "Environment setup complete. Activate with: conda activate creepyai25ENV"
