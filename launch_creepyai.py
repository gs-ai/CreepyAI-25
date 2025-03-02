#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI Launcher Script
========================

This script checks that all requirements are met and then launches
the CreepyAI application. It handles common setup issues and provides
helpful error messages.
"""

import os
import sys
import platform
import subprocess
import importlib.util
import logging
import traceback

# Set up logging
logger = logging.getLogger("creepyai_launcher")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher.log"))
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

def check_python_version():
    """Check Python version is compatible"""
    logger.info(f"Checking Python version: {sys.version}")
    if sys.version_info < (3, 6):
        logger.error(f"Incompatible Python version: {sys.version}")
        print("ERROR: CreepyAI requires Python 3.6 or higher")
        return False
    return True

def check_module(module_name):
    """Check if a module is installed"""
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception as e:
        logger.error(f"Error checking for module {module_name}: {str(e)}")
        return False

def check_required_modules():
    """Check all required modules are installed"""
    required_modules = [
        "PyQt5", 
        "yapsy", 
        "configobj", 
        "PIL"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing required modules: {', '.join(missing_modules)}")
        print("ERROR: The following required modules are missing:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install them using:")
        print("  conda install -c conda-forge pyqt")
        print("  pip install yapsy configobj Pillow")
        return False
    
    logger.info("All required modules are present")
    return True

def check_folder_structure():
    """Check necessary folders exist"""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CreepyAI-25', 'creepy')
    
    if not os.path.exists(app_path):
        logger.error(f"Cannot find application folder at {app_path}")
        print(f"ERROR: Cannot find CreepyAI application folder at {app_path}")
        return False
        
    # Create required directories if they don't exist
    for folder in ['projects', 'temp', 'logs']:
        folder_path = os.path.join(app_path, folder)
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                logger.info(f"Created folder: {folder_path}")
                print(f"Created folder: {folder_path}")
            except Exception as e:
                logger.error(f"Cannot create folder {folder_path}: {str(e)}")
                print(f"ERROR: Cannot create folder {folder_path}: {str(e)}")
                return False
    
    return True

def launch_app():
    """Launch the CreepyAI application"""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CreepyAI-25', 'creepy')
    main_script = os.path.join(app_path, 'CreepyMain.py')
    
    if not os.path.exists(main_script):
        logger.error(f"Cannot find main script at {main_script}")
        print(f"ERROR: Cannot find main script at {main_script}")
        return False
    
    print("Launching CreepyAI...")
    logger.info("Launching CreepyAI...")
    
    # Change to the app directory
    os.chdir(app_path)
    
    # Execute the app
    try:
        if platform.system() == "Windows":
            subprocess.Popen(['python', main_script])
        else:
            subprocess.Popen(['python3', main_script])
        logger.info("Application started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to launch CreepyAI: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: Failed to launch CreepyAI: {str(e)}")
        return False

def main():
    """Main function to launch the application"""
    print("CreepyAI Launcher")
    print("================\n")
    logger.info("Starting CreepyAI launcher")
    
    # Perform checks
    if not check_python_version():
        return 1
        
    if not check_required_modules():
        return 1
        
    if not check_folder_structure():
        return 1
        
    # Launch the app
    if not launch_app():
        return 1
        
    print("CreepyAI started successfully!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"ERROR: An unexpected error occurred: {str(e)}")
        sys.exit(1)
