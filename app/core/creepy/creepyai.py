#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI - Main Application Entry Point

This script initializes the CreepyAI application, handling setup,
logging configuration, dependency management, and launching the GUI.
"""

import sys
import os
import logging
import logging.config
import json
import importlib
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Configure a basic logger for startup errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
startup_logger = logging.getLogger("creepyai-startup")

# Application constants
DEFAULT_CONFIG_DIR = "config"
REQUIRED_DEPENDENCIES = {
    "PyQt5": "pyqt5",
    "yaml": "pyyaml",
    "psutil": "psutil",
    "colorama": "colorama"
}

def add_project_to_path() -> None:
    """Add the project directory to the Python path if needed."""
    project_dir = Path(__file__).parent.absolute()
    if str(project_dir) not in sys.path:
        startup_logger.debug(f"Adding {project_dir} to Python path")
        sys.path.insert(0, str(project_dir))

def load_json_config(config_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON configuration file.
    
    Args:
        config_path: Path to the JSON config file
        
    Returns:
        Dictionary of configuration values
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        json.JSONDecodeError: If the config file contains invalid JSON
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        startup_logger.error(f"Config file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        startup_logger.error(f"Invalid JSON in config file {config_path}: {e}")
        raise

def validate_logging_config(config: Dict[str, Any]) -> bool:
    """
    Validate the logging configuration structure.
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        True if the configuration is valid, False otherwise
    """
    required_keys = ['version', 'formatters', 'handlers', 'loggers']
    
    if not all(key in config for key in required_keys):
        missing_keys = [key for key in required_keys if key not in config]
        startup_logger.error(f"Invalid logging config: missing required keys {missing_keys}")
        return False
        
    # Check version (must be 1 for Python's logging.config)
    if config.get('version') != 1:
        startup_logger.error("Invalid logging config: version must be 1")
        return False
        
    # Check if root logger is defined
    if 'root' not in config.get('loggers', {}) and 'root' not in config:
        startup_logger.warning("Root logger not defined in config")
        
    return True

def get_logging_config() -> Optional[Dict[str, Any]]:
    """
    Load and validate the logging configuration.
    
    Returns:
        Validated logging configuration or None if invalid
    """
    try:
        # Try to import the configuration
        from config import logging_config
        
        # If it's a dict, use it directly
        if isinstance(logging_config, dict):
            config = logging_config
        # If it's a path, load the file
        elif isinstance(logging_config, str) and os.path.exists(logging_config):
            config = load_json_config(logging_config)
        else:
            startup_logger.error("Invalid logging configuration format")
            return None
            
        # Validate the configuration
        if validate_logging_config(config):
            return config
        return None
        
    except (ImportError, FileNotFoundError, json.JSONDecodeError) as e:
        startup_logger.error(f"Error loading logging configuration: {e}")
        return None

def validate_app_config(config: Dict[str, Any]) -> bool:
    """
    Validate the application configuration.
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        True if the configuration is valid, False otherwise
    """
    required_keys = ['app_name', 'version']
    
    if not all(key in config for key in required_keys):
        missing_keys = [key for key in required_keys if key not in config]
        startup_logger.error(f"Invalid app config: missing required keys {missing_keys}")
        return False
        
    return True

def get_app_config() -> Dict[str, Any]:
    """
    Load and validate the application configuration.
    
    Returns:
        Application configuration dictionary (with defaults if needed)
    """
    default_config = {
        'app_name': 'CreepyAI',
        'version': '1.0.0',
        'debug_mode': False,
        'enable_plugins': True,
        'plugin_dir': 'plugins',
        'data_dir': 'data'
    }
    
    try:
        # Try to import the configuration
        from config import app_config
        
        # If it's a dict, use it directly
        if isinstance(app_config, dict):
            config = app_config
        # If it's a path, load the file
        elif isinstance(app_config, str) and os.path.exists(app_config):
            config = load_json_config(app_config)
        else:
            startup_logger.warning("Invalid app configuration format, using defaults")
            return default_config
            
        # Validate the configuration
        if validate_app_config(config):
            # Merge with defaults for any missing keys
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
        
        startup_logger.warning("Invalid app configuration, using defaults")
        return default_config
        
    except (ImportError, FileNotFoundError, json.JSONDecodeError) as e:
        startup_logger.warning(f"Error loading app configuration: {e}. Using defaults.")
        return default_config

def setup_logging() -> logging.Logger:
    """
    Set up logging configuration and return a logger for the main module.
    
    Returns:
        Configured logger instance
    """
    # Try to load and apply logging configuration
    logging_config = get_logging_config()
    
    if logging_config:
        # Apply the loaded configuration
        try:
            logging.config.dictConfig(logging_config)
            startup_logger.info("Logging configuration applied successfully")
        except (ValueError, TypeError, AttributeError) as e:
            startup_logger.error(f"Error applying logging configuration: {e}")
            # Fallback to basic config below
    else:
        startup_logger.warning("Using default logging configuration")
    
    # Get a logger for the main module
    logger = logging.getLogger(__name__)
    
    # Set level based on app config
    app_config = get_app_config()
    if app_config.get('debug_mode', False):
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    return logger

def check_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if required dependencies are installed.
    
    Returns:
        Tuple of (all_dependencies_installed, list_of_missing_dependencies)
    """
    missing = []
    
    for module_name, pip_package in REQUIRED_DEPENDENCIES.items():
        try:
            # Try to import the module
            importlib.import_module(module_name)
        except ImportError:
            missing.append((module_name, pip_package))
    
    return len(missing) == 0, missing

def install_dependencies(missing_deps: List[Tuple[str, str]], auto_install: bool = False) -> bool:
    """
    Install missing dependencies using pip.
    
    Args:
        missing_deps: List of tuples (module_name, pip_package)
        auto_install: Whether to install automatically without prompting
        
    Returns:
        True if all dependencies were installed successfully, False otherwise
    """
    if not missing_deps:
        return True
        
    print("\n--- Missing Dependencies ---")
    for module_name, pip_package in missing_deps:
        print(f" - {module_name} (pip package: {pip_package})")
    
    # If auto-install is enabled, proceed without asking
    if not auto_install:
        choice = input("\nWould you like to install these dependencies now? (y/n): ").strip().lower()
        if choice != 'y':
            print("Aborted. Please install the dependencies manually.")
            return False
    
    print("\nInstalling dependencies...")
    
    for _, pip_package in missing_deps:
        try:
            print(f"Installing {pip_package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {pip_package}: {e}")
            return False
    
    print("\nAll dependencies installed successfully!")
    return True

def main() -> int:
    """
    Main application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Add project directory to Python path if needed
    add_project_to_path()
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        # Try to install dependencies
        if not install_dependencies(missing_deps):
            print("\nCould not install required dependencies. Please install them manually:")
            for _, pip_package in missing_deps:
                print(f"  pip install {pip_package}")
            return 1
        
        # Verify dependencies again after installation
        deps_ok, still_missing = check_dependencies()
        if not deps_ok:
            print("\nSome dependencies are still missing after installation:")
            for module_name, pip_package in still_missing:
                print(f" - {module_name} (pip package: {pip_package})")
            return 1
    
    # Set up logging
    logger = setup_logging()
    
    # Get application configuration
    app_config = get_app_config()
    app_name = app_config.get('app_name', 'CreepyAI')
    app_version = app_config.get('version', '1.0.0')
    
    logger.info(f"Initializing {app_name} v{app_version}")
    
    try:
        # Check if we have GUI or CLI arguments
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', '-c', '--cli']:
            # Handle CLI mode
            return handle_cli_mode(sys.argv[1:], app_config)
        else:
            # Default to GUI mode
            return launch_gui(app_config)
            
    except Exception as e:
        logger.critical(f"Fatal error starting CreepyAI: {e}", exc_info=True)
        return 1

def handle_cli_mode(args: List[str], app_config: Dict[str, Any]) -> int:
    """
    Handle command-line interface mode.
    
    Args:
        args: Command line arguments
        app_config: Application configuration
        
    Returns:
        Exit code
    """
    logger = logging.getLogger(__name__)
    logger.info("Running in CLI mode")
    
    # Import the CLI handler
    try:
        from cli import cli_handler
        return cli_handler.run(args, app_config)
    except ImportError:
        logger.error("CLI module not available")
        print("CLI mode not available. Please install the CLI module.")
        return 1

def launch_gui(app_config: Dict[str, Any]) -> int:
    """
    Launch the application GUI.
    
    Args:
        app_config: Application configuration
        
    Returns:
        Exit code
    """
    logger = logging.getLogger(__name__)
    logger.info("Launching GUI")
    
    try:
        # Import PyQt5 and the main application window
        from PyQt5 import QtWidgets
        from ui import CreepyAIApp
        
        # Create and run the application
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName(app_config.get('app_name', 'CreepyAI'))
        app.setApplicationVersion(app_config.get('version', '1.0.0'))
        
        # Set application style if specified
        if 'app_style' in app_config:
            app.setStyle(app_config['app_style'])
        
        # Create main window
        main_window = CreepyAIApp(app_config)
        main_window.show()
        
        logger.info("Application GUI started")
        return app.exec_()
        
    except Exception as e:
        logger.critical(f"Error launching GUI: {e}", exc_info=True)
        print(f"Error launching GUI: {e}")
        print("Make sure PyQt5 is installed correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
