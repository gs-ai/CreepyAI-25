#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI - OSINT Intelligence Gathering Tool

This is the main entry point for the CreepyAI application.
It handles command-line arguments and launches the appropriate interface.
"""

import os
import sys
import argparse
import logging
import configparser
from pathlib import Path
import time
import platform
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='creepyai.log'
)
logger = logging.getLogger('CreepyAI')

def get_app_directories():
    """Get application directories for config, data, etc."""
    home_dir = str(Path.home())
    
    app_dirs = {
        'config_dir': os.path.join(home_dir, '.creepyai'),
        'projects_dir': os.path.join(home_dir, 'CreepyAI_Projects'),
        'temp_dir': os.path.join(home_dir, '.creepyai', 'tmp'),
        'plugins_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'creepy', 'plugins')
    }
    
    return app_dirs

def ensure_directories(dirs):
    """Ensure all required directories exist, create if necessary"""
    for name, path in dirs.items():
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                logger.info(f"Created directory: {path}")
            except OSError as e:
                logger.error(f"Failed to create directory {path}: {e}")
                return False
    
    return True

def create_default_config(config_path):
    """Create default configuration file if it doesn't exist"""
    if os.path.exists(config_path):
        return True
    
    config = configparser.ConfigParser()
    config['General'] = {
        'first_run': 'True',
        'check_for_updates': 'True',
        'projects_directory': get_app_directories()['projects_dir']
    }
    
    config['Plugins'] = {
        'enable_all': 'False'
    }
    
    try:
        with open(config_path, 'w') as config_file:
            config.write(config_file)
        logger.info(f"Created default configuration at {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create default configuration: {e}")
        return False

def setup_application():
    """Setup application directories, configurations and resources"""
    logger.info("Setting up CreepyAI application")
    
    # Create required directories
    ensure_directories_exist()
    
    # Initialize plugin system
    init_plugin_system()
    
    # Set application style
    setup_application_style()
    
    # Check for updates
    check_for_updates()
    
    return True

def ensure_directories_exist():
    """Ensure all required directories exist"""
    required_dirs = [
        'temp', 
        'projects', 
        'logs', 
        'cache', 
        'exports'
    ]
    
    for directory in required_dirs:
        dir_path = os.path.join(os.getcwd(), directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"Created directory: {dir_path}")
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

def init_plugin_system():
    """Initialize plugin system and verify plugins"""
    from utilities.PluginManager import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.load_plugins()

    # Example of initializing a specific plugin
    plugin_manager.initialize_plugin('example_plugin')
    
    # Count loaded plugins
    plugins = plugin_manager.get_all_plugins()
    logger.info(f"Loaded {len(plugins)} plugins")
    
    # Check for plugin configuration issues
    config_issues = []
    for plugin in plugins:
        try:
            config_status = plugin.is_configured()
            if not config_status[0]:
                config_issues.append(f"{plugin.name}: {config_issues[1]}")
        except Exception as e:
            config_issues.append(f"{plugin.name}: Error checking configuration - {str(e)}")
    
    if config_issues:
        logger.warning(f"Found {len(config_issues)} plugin configuration issues:")
        for issue in config_issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("All plugins are properly configured")
        
def setup_application_style():
    """Setup application style and theme"""
    try:
        # Load QSS style file
        style_path = os.path.join(os.getcwd(), 'creepy', 'include', 'style.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                style = f.read()
                
            # Apply style
            from PyQt5.QtWidgets import QApplication
            if QApplication.instance():
                QApplication.instance().setStyleSheet(style)
                logger.info("Applied application style from QSS")
        else:
            logger.warning(f"Style file not found at {style_path}")
            
    except Exception as e:
        logger.error(f"Failed to apply application style: {str(e)}")
        
def check_for_updates():
    """Check for application updates"""
    # This is a placeholder for update checking functionality
    logger.info("Checking for updates")
    # Implementation would typically connect to a server to check versions
    # For now, we'll just log the action

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='CreepyAI - OSINT Intelligence Gathering Tool',
        epilog='For more information, visit: https://github.com/gs-ai/CreepyAI-25'
    )
    
    # Add arguments
    parser.add_argument('-g', '--gui', action='store_true', help='Launch the graphical user interface')
    parser.add_argument('-c', '--cli', action='store_true', help='Use command line interface')
    parser.add_argument('-t', '--target', help='Target for intelligence gathering')
    parser.add_argument('-o', '--output', help='Output directory for results')
    parser.add_argument('-p', '--profile', choices=['basic', 'full', 'social', 'professional', 'custom'], 
                      help='Profile type to use for gathering intelligence')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

def launch_gui():
    """Launch the graphical user interface"""
    try:
        import tkinter as tk
        try:
            from .gui import CreepyAIGUI
        except ImportError as e:
            logger.error(f"Failed to import GUI module: {e}")
            print("Error: Could not load GUI module. Make sure creepyai_gui is available.")
            sys.exit(1)
        
        root = tk.Tk()
        app = CreepyAIGUI(root)
        root.mainloop()
    except ImportError as e:
        logger.error(f"Failed to import GUI dependencies: {e}")
        print("Error: Could not load GUI dependencies. Make sure tkinter is installed.")
        print("Try: pip install tk")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error launching GUI: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def launch_cli(args):
    """Launch command line interface with the given arguments"""
    try:
        print("CreepyAI CLI mode")
