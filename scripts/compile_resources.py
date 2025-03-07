#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to compile QRC resources into Python modules
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ResourceCompiler')

def compile_resources(qrc_path, output_path=None):
    """
    Compile a QRC file into a Python module using pyrcc5
    
    Args:
        qrc_path: Path to the QRC file
        output_path: Path for the output Python file (default: same directory as QRC)
    
    Returns:
        bool: True if compilation was successful
    """
    if not os.path.exists(qrc_path):
        logger.error(f"QRC file not found: {qrc_path}")
        return False
    
    # If output path is not specified, use the QRC directory
    if not output_path:
        output_path = os.path.splitext(qrc_path)[0] + '_rc.py'
    
    try:
        # Try using pyrcc5 directly
        command = ['pyrcc5', '-o', output_path, qrc_path]
        logger.info(f"Running command: {' '.join(command)}")
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"pyrcc5 failed: {result.stderr}")
            
            # Try using PyQt5 tools if installed as a module
            logger.info("Trying with PyQt5 tools...")
            from PyQt5.pyrcc_main import main as pyrcc_main
            
            # Backup sys.argv and replace with our command
            old_argv = sys.argv
            sys.argv = ['pyrcc5', '-o', output_path, qrc_path]
            
            try:
                pyrcc_main()
                logger.info(f"Resources compiled to {output_path}")
                return True
            except Exception as e:
                logger.error(f"PyQt5 tools failed: {str(e)}")
                return False
            finally:
                sys.argv = old_argv
        else:
            logger.info(f"Resources compiled to {output_path}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to compile resources: {str(e)}")
        return False

if __name__ == "__main__":
    # Get project root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Default QRC file
    qrc_file = os.path.join(project_dir, "resources", "creepy_resources.qrc")
    
    # Output Python module
    output_file = os.path.join(project_dir, "resources", "creepy_resources_rc.py")
    
    # Allow command line override
    if len(sys.argv) > 1:
        qrc_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    # Compile the resources
    if compile_resources(qrc_file, output_file):
        print(f"Successfully compiled {qrc_file} to {output_file}")
        sys.exit(0)
    else:
        print(f"Failed to compile {qrc_file}")
        sys.exit(1)
