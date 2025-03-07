#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qt environment setup for CreepyAI.

This module configures the Qt environment and provides helper functions
for working with Qt in the application.
"""

import os
import sys
import logging

logger = logging.getLogger('CreepyAI.QtSetup')

def setup_qt_environment():
    """Set up the Qt environment with necessary configurations."""
    # Set environment variables for Qt
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Fix for macOS Retina display
    if sys.platform == "darwin":
        os.environ["QT_SCALE_FACTOR"] = "1"
    
    # Fix for WebEngine on macOS
    if sys.platform == "darwin":
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--single-process"
    
    logger.info("Qt environment configured")

def load_stylesheet(name="dark"):
    """Load a QSS stylesheet for the application.
    
    Args:
        name: Name of the stylesheet (without extension)
        
    Returns:
        str: The stylesheet content
    """
    try:
        # Try to load from compiled resources first
        from PyQt5.QtCore import QFile, QTextStream
        import creepyai_rc
        
        file = QFile(f":styles/{name}.qss")
        if file.exists() and file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            file.close()
            return stylesheet
    except ImportError:
        logger.warning("Could not load stylesheet from resources, trying filesystem")
    
    # Fallback to filesystem
    try:
        stylesheet_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "resources", "styles", f"{name}.qss"
        )
        with open(stylesheet_path, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load stylesheet: {e}")
        return ""
