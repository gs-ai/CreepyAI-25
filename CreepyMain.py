#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import creepy_resources_rc
import os
import argparse
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

# Add project root to path
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path)

# Import core components
from core.logger import setup_logger
from core.config_manager import ConfigManager
from core.check_compatibility import check_compatibility
from core.install_dependencies import install_missing_dependencies

# Import UI components
from creepy.ui.creepyai_gui import CreepyMainWindow

def parse_arguments():
    parser = argparse.ArgumentParser(description='CreepyAI - OSINT Geolocation Tool')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-c', '--config', help='Path to config file')
    parser.add_argument('-p', '--project', help='Project file to open')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI (for automated tasks)')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(log_level=log_level)
    
    logger.info("Starting CreepyAI...")
    
    # Check compatibility and install dependencies if needed
    if not check_compatibility():
        logger.warning("System compatibility issues detected. Attempting to fix...")
        install_missing_dependencies()
    
    # Initialize configuration
    config_manager = ConfigManager(args.config)
    
    if args.no_gui:
        # CLI mode
        logger.info("Running in command-line mode")
        # Process CLI commands here
        # ...
    else:
        # GUI mode
        app = QApplication(sys.argv)
        app.setApplicationName("CreepyAI")
        app.setOrganizationName("CreepyAI")
        
        # Show splash screen
        splash_path = os.path.join(app_path, "creepy", "resources", "splash.png")
        if os.path.exists(splash_path):
            splash_pixmap = QPixmap(splash_path)
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            app.processEvents()
        else:
            splash = None
        
        # Create and show the main window
        main_window = CreepyMainWindow(config_manager)
        
        # If a project was specified, open it
        if args.project and os.path.exists(args.project):
            # Use a timer to open the project after the UI is fully loaded
            def open_project():
                main_window.open_project(args.project)
            
            QTimer.singleShot(500, open_project)
        
        # Hide splash and show main window
        if splash:
            QTimer.singleShot(1500, splash.close)
            QTimer.singleShot(1600, main_window.show)
        else:
            main_window.show()
        
        # Start the event loop
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
