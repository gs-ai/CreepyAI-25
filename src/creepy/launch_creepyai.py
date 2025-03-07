#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI Launcher Script

This script initializes the environment and launches CreepyAI
with the appropriate UI interface.
"""

import argparse
import logging
import os
import sys
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CreepyAI Launcher')

def setup_environment():
    """Set up the application environment before launch."""
    # Import and run Qt environment setup
    try:
        from qt_setup import setup_qt_environment
        if not setup_qt_environment():
            logger.warning("Qt environment setup failed, continuing anyway...")
    except ImportError:
        logger.warning("qt_setup module not found, skipping Qt environment setup")

def launch_pyqt5_ui():
    """Launch the PyQt5 UI version."""
    logger.info("Launching PyQt5 UI")
    print("Starting CreepyAI with PyQt5 interface...")
    
    try:
        # Import and run the PyQt5 UI
        from gui.pyqt5_ui import main as pyqt5_main
        pyqt5_main()
    except ImportError as e:
        logger.error(f"Failed to import PyQt5 UI: {e}")
        print("Error: PyQt5 UI components not found. Make sure PyQt5 is installed.")
        return False
    except Exception as e:
        logger.error(f"Error launching PyQt5 UI: {e}")
        print(f"Error launching PyQt5 UI: {e}")
        return False
    
    return True

def launch_tkinter_ui():
    """Launch the Tkinter UI version."""
    logger.info("Launching Tkinter UI")
    print("Starting CreepyAI with Tkinter interface...")
    
    try:
        # Import and run the Tkinter UI
        from gui.tkinter_ui import main as tk_main
        tk_main()
    except ImportError as e:
        logger.error(f"Failed to import Tkinter UI: {e}")
        print("Error: Tkinter UI components not found.")
        return False
    except Exception as e:
        logger.error(f"Error launching Tkinter UI: {e}")
        print(f"Error launching Tkinter UI: {e}")
        return False
    
    return True

def main():
    """Main entry point for the launcher."""
    parser = argparse.ArgumentParser(description='Launch CreepyAI')
    parser.add_argument('--ui', choices=['pyqt5', 'tkinter'], default='pyqt5',
                        help='User interface to use (default: pyqt5)')
    parser.add_argument('--diagnose-qt', action='store_true',
                        help='Run Qt diagnostics and exit')
    args = parser.parse_args()
    
    # Set up the environment
    setup_environment()
    
    # Run Qt diagnostics if requested
    if args.diagnose_qt:
        try:
            from qt_setup import diagnose_qt_issues
            print("Running Qt diagnostics:")
            issues = diagnose_qt_issues()
            for issue in issues:
                print(f"- {issue}")
            return 0
        except ImportError:
            print("Error: qt_setup module not found")
            return 1
    
    # Get available UIs
    available_uis = []
    try:
        import PyQt5
        available_uis.append('pyqt5')
    except ImportError:
        pass
    
    try:
        import tkinter
        available_uis.append('tkinter')
    except ImportError:
        pass
    
    logger.info(f"Available UIs: {available_uis}")
    
    # Launch requested UI
    if args.ui == 'pyqt5':
        if 'pyqt5' in available_uis:
            if not launch_pyqt5_ui():
                return 1
        else:
            logger.error("PyQt5 UI requested but PyQt5 is not installed")
            print("Error: PyQt5 is not installed. Install it with 'pip install PyQt5 PyQtWebEngine'")
            return 1
    elif args.ui == 'tkinter':
        if 'tkinter' in available_uis:
            if not launch_tkinter_ui():
                return 1
        else:
            logger.error("Tkinter UI requested but Tkinter is not available")
            print("Error: Tkinter is not available in this Python installation")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
