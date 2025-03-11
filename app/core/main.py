#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for CreepyAI application.
Handles initialization, environment setup, and application startup.
"""
import os
import sys
import logging
import argparse
import traceback
from typing import Dict, List, Any, Optional, Union

# Add the project root to path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import core modules
from app.core.path_utils import get_app_root, ensure_app_dirs
from app.core.import_helper import ensure_imports
from app.core.logger import setup_logger
from app.core.initialization import initialize_application
from app.core.engine import CreepyAIEngine
from app.core.config import Configuration
from app.core.utils import get_system_info

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='CreepyAI - OSINT and data analysis platform')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-plugins', action='store_true', help='Disable plugins')
    parser.add_argument('--gui', action='store_true', help='Launch the GUI (default)')
    parser.add_argument('--cli', action='store_true', help='Launch in CLI mode')
    parser.add_argument('--check', action='store_true', help='Run system check only')
    parser.add_argument('--quiet', action='store_true', help='Minimal console output')
    
    return parser.parse_args()

def setup_environment():
    """Set up the application environment."""
    # Make sure we're starting from the project root
    app_root = get_app_root()
    os.chdir(app_root)
    
    # Ensure all directories exist
    app_dirs = ensure_app_dirs()
    
    # Set up import paths
    ensure_imports()
    
    return app_root, app_dirs

def check_system():
    """Run system check and report issues."""
    print("Running CreepyAI system check...")
    
    # Get system information
    system_info = get_system_info()
    print("\nSystem Information:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("\n⚠️ WARNING: CreepyAI requires Python 3.7 or higher.")
        print(f"Current Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"\n✅ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is compatible.")
    
    # Check required directories
    app_dirs = ensure_app_dirs()
    print("\nDirectory Structure:")
    for dir_type, dir_path in app_dirs.items():
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_type}: {dir_path}")
        else:
            print(f"  ❌ {dir_type}: {dir_path} (not found)")
    
    # Check for required modules
    required_modules = ['PyQt5', 'yaml', 'pathlib', 'requests']
    print("\nRequired Modules:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (not installed)")
    
    # Create the engine to test basic functionality
    try:
        engine = CreepyAIEngine()
        print("\n✅ Core engine initialized successfully.")
    except Exception as e:
        print("\n❌ Failed to initialize core engine:")
        print(f"   {str(e)}")
    
    print("\nSystem check complete.")

def run_application(args):
    """Run the CreepyAI application."""
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    if args.quiet:
        log_level = logging.WARNING
        
    logger = setup_logger('creepyai', level=log_level)
    logger.info("Starting CreepyAI")
    
    try:
        # Initialize the application
        init_info = initialize_application(config_path=args.config)
        logger.debug(f"Initialization info: {init_info}")
        
        # Create the engine
        engine = CreepyAIEngine(config_path=init_info['config_path'])
        
        # Load plugins if enabled
        if not args.no_plugins:
            logger.info("Loading plugins...")
            try:
                engine.load_plugins()
            except Exception as e:
                logger.error(f"Plugin loading failed: {e}")
        
        # Determine running mode and launch the appropriate interface
        if args.cli:
            logger.info("Starting CLI mode")
            run_cli_mode(engine, init_info)
        else:
            logger.info("Starting GUI mode")
            run_gui_mode(engine, init_info)
            
        return True
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def run_cli_mode(engine, init_info):
    """Run the application in CLI mode."""
    try:
        from app.cli.handler.cli_handler import CLIHandler
        cli = CLIHandler(engine=engine)
        cli.run()
    except ImportError as e:
        logging.error(f"Failed to import CLI modules: {e}")
        print("Error: CLI modules not found.")
        print("Try running with --gui flag instead.")
        sys.exit(1)

def run_gui_mode(engine, init_info):
    """Run the application in GUI mode."""
    try:
        from PyQt5.QtWidgets import QApplication
        
        # Try multiple import paths until we find the GUI
        gui_class = None
        try:
            # First try from the ui.main module (new structured path)
            from ui.main import CreepyAIGUI
            gui_class = CreepyAIGUI
        except ImportError:
            try:
                # Then try from app.gui.ui.main module
                from app.gui.ui.main import CreepyAIGUI
                gui_class = CreepyAIGUI
            except ImportError:
                try:
                    # Then try direct import from main gui folder
                    from app.gui.main.creepyai_gui import CreepyAIGUI
                    gui_class = CreepyAIGUI
                except ImportError:
                    try:
                        # Finally try the fixed version
                        from app.gui.main.creepyai_gui_fixed import CreepyAIGUI
                        gui_class = CreepyAIGUI
                    except ImportError:
                        logging.error("Could not import main GUI class")
                        print("Could not import main GUI class")
                        print("Try reinstalling PyQt5 or running with --cli flag.")
                        sys.exit(1)
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("CreepyAI")
        app.setOrganizationName("CreepyAI Team")
        
        # Create main window
        main_window = gui_class(engine=engine)
        main_window.show()
        
        # Run the application event loop
        sys.exit(app.exec_())
            
    except ImportError as e:
        logging.error(f"Failed to import GUI modules: {e}")
        print("Error: GUI dependencies not found.")
        print("Try installing PyQt5 with 'pip install PyQt5' or run with --cli flag.")
        sys.exit(1)

def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up environment
    app_root, app_dirs = setup_environment()
    
    # Run system check if requested
    if args.check:
        check_system()
        return 0
    
    # Run the application
    success = run_application(args)
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
