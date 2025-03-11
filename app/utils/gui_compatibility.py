#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GUI compatibility utilities for CreepyAI

Provides compatibility functions for GUI-related functionality
"""

import logging
import sys
import os

logger = logging.getLogger(__name__)

# Detect which GUI frameworks are available
PYQT_AVAILABLE = False
TKINTER_AVAILABLE = False

try:
    from PyQt5.QtWidgets import QPushButton, QApplication
    from PyQt5.QtCore import pyqtSignal, QObject
    PYQT_AVAILABLE = True
except ImportError:
    logger.debug("PyQt5 not available")

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    logger.debug("Tkinter not available")

class ButtonFactory:
    """Factory for creating buttons with consistent styling"""
    
    @staticmethod
    def create_button(text, parent=None, tooltip=None):
        """Create a styled button"""
        button = QPushButton(text, parent)
        if tooltip:
            button.setToolTip(tooltip)
        button.resize(button.sizeHint())
        return button

def fix_tkinter_buttons_in_pyqt():
    """
    Fix compatibility issues between Tkinter and PyQt
    
    Some plugins may use Tkinter which can conflict with PyQt
    This function helps mitigate those issues
    """
    # This is just a placeholder for now
    pass
