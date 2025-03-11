#!/usr/bin/env python3
"""
Launch script for CreepyAI.
Sets up the Python environment and starts the application.
"""
import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional

# Add parent directory to path to allow importing core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.path_utils import get_app_root, ensure_app_dirs, get_user_log_dir
    from core.logger import setup_logger
    from core.initialization import initialize_application
    from core.import_helper import ensure_imports
except ImportError as e:
    print(f"Error importing core modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

logger = logging.getLogger('creepyai.launch')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Launch CreepyAI')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-plugins', action='store_true', help='Disable plugins')
    parser.add_argument('--gui', action='store_true', help='Launch the GUI (default)')
    parser.add_argument('--cli', action='store_true', help='Launch in CLI mode')
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_arguments()
    
    try:
        # Initialize the application
        init_info = initialize_application(config_path=args.config)
        
        # Configure logging based on debug flag
        log_level = logging.DEBUG if args.debug else logging.INFO
        setup_logger(log_dir=init_info['log_dir'], level=log_level)
        
        logger.info("Starting CreepyAI application")
        logger.debug(f"Initialization info: {init_info}")
        
        # Choose between GUI and CLI mode
        if args.cli:
            launch_cli_mode(init_info, not args.no_plugins)
        else:
            launch_gui_mode(init_info, not args.no_plugins)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)

def launch_gui_mode(init_info: Dict[str, Any], load_plugins: bool = True):
    """Launch the GUI application.
    
    Args:
        init_info: Initialization information
        load_plugins: Whether to load plugins
    """
    try:
        # Import GUI modules dynamically to avoid issues if GUI dependencies aren't installed
        from creepyai_gui import launch_gui
        
        # Launch GUI with configuration
        launch_gui(
            config_path=init_info['config_path'],
            app_root=init_info['app_root'],
            load_plugins=load_plugins
        )
    except ImportError:
        logger.error("Failed to import GUI modules. Make sure PyQt5 is installed.")
        print("Error: GUI dependencies not found. Install them with 'pip install PyQt5'")
        sys.exit(1)

def launch_cli_mode(init_info: Dict[str, Any], load_plugins: bool = True):
    """Launch the CLI application.
    
    Args:
        init_info: Initialization information
        load_plugins: Whether to load plugins
    """
    try:
        # Import CLI modules
        sys.path.insert(0, os.path.join(init_info['app_root'], 'src', 'cli', 'handler'))
        from cli_handler import CLIHandler
        
        # Create and run CLI handler
        cli = CLIHandler(
            config_path=init_info['config_path'],
            load_plugins=load_plugins
        )
        cli.run()
    except ImportError:
        logger.error("Failed to import CLI modules.")
        print("Error: CLI modules not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
