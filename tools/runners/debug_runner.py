#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug runner for CreepyAI application
This script provides more detailed debugging information
"""

import os
import sys
import logging
import traceback
import subprocess
from datetime import datetime

# Configure detailed logging
log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'creepyai_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('CreepyAI.Debug')

def check_environment():
    """Check the Python environment and dependencies"""
    logger.info("Checking environment...")
    
    # Python version
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # PyQt5 version
    try:
        import PyQt5
        logger.info(f"PyQt5 version: {PyQt5.QtCore.PYQT_VERSION_STR}")
        logger.info(f"Qt version: {PyQt5.QtCore.QT_VERSION_STR}")
    except ImportError as e:
        logger.error(f"PyQt5 import error: {e}")
    except Exception as e:
        logger.error(f"Error getting PyQt5 version: {e}")
    
    # Check for QtWebEngine
    try:
        from PyQt5 import QtWebEngineWidgets
        logger.info("QtWebEngineWidgets is available")
    except ImportError as e:
        logger.error(f"QtWebEngineWidgets import error: {e}")
    
    # Check other dependencies
    dependencies = ['yapsy', 'configobj']
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"{dep} is available")
        except ImportError:
            logger.warning(f"{dep} is not installed")

def check_resources():
    """Check if resources are available and correctly compiled"""
    logger.info("Checking resources...")
    
    # Check if resources directory exists
    resources_dir = os.path.join(os.getcwd(), 'resources')
    if os.path.isdir(resources_dir):
        logger.info(f"Resources directory exists: {resources_dir}")
        # List resources
        files = os.listdir(resources_dir)
        logger.info(f"Resources directory contains: {files}")
    else:
        logger.error(f"Resources directory not found: {resources_dir}")
    
    # Check for compiled resources
    rc_file = os.path.join(resources_dir, 'creepy_resources_rc.py')
    if os.path.isfile(rc_file):
        logger.info(f"Compiled resources file exists: {rc_file}")
        
        # Check if it's properly importable
        try:
            sys.path.insert(0, os.path.dirname(resources_dir))
            import resources.creepy_resources_rc
            logger.info("Resource module imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import resource module: {e}")
    else:
        logger.warning(f"Compiled resources file not found: {rc_file}")
        # Try to compile resources
        qrc_file = os.path.join(resources_dir, 'creepy_resources.qrc')
        if os.path.isfile(qrc_file):
            logger.info(f"QRC file exists, attempting to compile: {qrc_file}")
            try:
                result = subprocess.run(['pyrcc5', '-o', rc_file, qrc_file], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Resources compiled successfully")
                else:
                    logger.error(f"Resource compilation failed: {result.stderr}")
            except Exception as e:
                logger.error(f"Error running pyrcc5: {e}")
        else:
            logger.error(f"QRC file not found: {qrc_file}")

def test_basic_ui():
    """Test creating a basic PyQt window to verify UI functionality"""
    logger.info("Testing basic UI functionality...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
        
        app = QApplication([])
        window = QMainWindow()
        window.setWindowTitle("CreepyAI Test")
        window.setGeometry(100, 100, 400, 200)
        
        label = QLabel("UI Test Successful", window)
        label.setGeometry(100, 80, 200, 30)
        
        logger.info("Basic UI created successfully")
        
        window.show()
        logger.info("Window shown, checking if it's visible...")
        
        # Don't actually run the event loop in this test
        window.close()
        logger.info("Basic UI test completed")
        
        return True
    except Exception as e:
        logger.error(f"UI test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def run_creepyai_with_debug():
    """Run the CreepyAI application with additional debugging"""
    logger.info("Starting CreepyAI with debug mode...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Import the main module with additional error handling
        logger.info("Importing CreepyMain...")
        
        # Instead of directly importing, we'll use a safer approach
        try:
            # First import will verify it loads
            import creepy.CreepyMain as CreepyMain
            
            # Now run the Qt app with a custom main
            from PyQt5.QtWidgets import QApplication
            
            # Initialize app
            app = QApplication(sys.argv)
            
            # Create main window with exception handling
            logger.info("Creating main window...")
            try:
                main_window = CreepyMain.MainWindow()
                logger.info("Main window created successfully")
                
                # Show the window
                logger.info("Showing main window...")
                main_window.show()
                logger.info("Main window show() called")
                
                # Run the application
                logger.info("Starting application main loop...")
                return app.exec_()
                
            except Exception as e:
                logger.error(f"Error creating/showing main window: {e}")
                logger.error(traceback.format_exc())
                return 1
                
        except Exception as e:
            logger.error(f"Error importing CreepyMain: {e}")
            logger.error(traceback.format_exc())
            return 1
            
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        return 1

def main():
    """Main function for debug runner"""
    logger.info("="*50)
    logger.info("CreepyAI Debug Runner Started")
    logger.info("="*50)
    
    # Check environment
    check_environment()
    
    # Check resources
    check_resources()
    
    # Test basic UI
    ui_test_result = test_basic_ui()
    if not ui_test_result:
        logger.error("Basic UI test failed, may not be able to run CreepyAI")
    
    # Run the application
    logger.info("="*50)
    logger.info("Starting CreepyAI Application")
    logger.info("="*50)
    
    result = run_creepyai_with_debug()
    
    logger.info("="*50)
    logger.info(f"CreepyAI Application Exited with code {result}")
    logger.info("="*50)
    
    return result

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Critical error in debug runner: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)
