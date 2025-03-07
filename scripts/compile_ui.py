#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compile UI files for CreepyAI

This script compiles .ui files to Python code using PyQt5's uic module.
"""

import os
import glob
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compile_ui_file(ui_file, py_file):
    """Compile a .ui file to a Python file."""
    try:
        # Try using PyQt5 uic module
        from PyQt5 import uic
        with open(py_file, 'w', encoding='utf-8') as f:
            uic.compileUi(ui_file, f)
        logger.info(f"Compiled {ui_file} to {py_file}")
        return True
    except ImportError:
        logger.warning("PyQt5 uic not available, trying pyuic5 command")
        
        # Fall back to pyuic5 command
        try:
            result = subprocess.run(['pyuic5', '-o', py_file, ui_file], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Compiled {ui_file} to {py_file} using pyuic5")
                return True
            else:
                logger.error(f"pyuic5 failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to run pyuic5: {e}")
            return False

def compile_ui_files(ui_dir='resources/ui', output_dir='gui/ui'):
    """Compile all .ui files in ui_dir to Python files in output_dir."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .ui files
    ui_files = glob.glob(os.path.join(ui_dir, '*.ui'))
    if not ui_files:
        logger.warning(f"No .ui files found in {ui_dir}")
        return False
    
    # Compile each file
    success_count = 0
    for ui_file in ui_files:
        basename = os.path.splitext(os.path.basename(ui_file))[0]
        py_file = os.path.join(output_dir, f"{basename}.py")
        if compile_ui_file(ui_file, py_file):
            success_count += 1
    
    # Create __init__.py if it doesn't exist
    init_file = os.path.join(output_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('"""UI module for CreepyAI."""\n')
    
    logger.info(f"Compiled {success_count} of {len(ui_files)} UI files")
    return success_count == len(ui_files)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Compile UI files for CreepyAI')
    parser.add_argument('--ui-dir', default='resources/ui',
                        help='Directory containing .ui files (default: resources/ui)')
    parser.add_argument('--output-dir', default='gui/ui',
                        help='Output directory for Python files (default: gui/ui)')
    args = parser.parse_args()
    
    if compile_ui_files(args.ui_dir, args.output_dir):
        print("UI compilation completed successfully")
    else:
        print("UI compilation completed with errors")
