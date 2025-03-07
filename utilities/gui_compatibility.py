#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Compatibility layer for GUI frameworks.
Provides consistent button creation and handling whether using PyQt5 or Tkinter.
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
    """Factory for creating buttons with consistent styles"""
    
    @staticmethod
    def create_button(text, parent=None):
        button = QPushButton(text, parent)
        button.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; }")
        return button

def fix_tkinter_buttons_in_pyqt():
    """Fix compatibility issues between Tkinter and PyQt buttons"""
    import tkinter as tk
    from PyQt5.QtWidgets import QApplication
    
    def on_tk_button_click():
        app = QApplication.instance()
        if app:
            app.processEvents()
    
    tk.Button.bind('<Button-1>', lambda event: on_tk_button_click())
