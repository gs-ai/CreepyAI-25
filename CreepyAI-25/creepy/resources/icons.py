#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt5.QtGui import QIcon, QPixmap

class Icons:
    """Helper class to provide fallback icons in case resource file is not properly loaded"""

    ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "images")

    @staticmethod
    def get_icon(name):
        """Get an icon either from resources or from filesystem"""
        # Try from resources first (prefix with 'creepy/')
        icon = QIcon(f":/creepy/{name}")
        
        # If the icon is empty, try to load from file
        if icon.isNull():
            icon_path = os.path.join(Icons.ICON_DIR, f"{name}.png")
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
            else:
                # Return a blank icon rather than None to avoid crashes
                icon = QIcon()
                
        return icon

    @staticmethod
    def get_pixmap(name):
        """Get a pixmap either from resources or from filesystem"""
        # Try from resources first
        pixmap = QPixmap(f":/creepy/{name}")
        
        # If the pixmap is empty, try to load from file
        if pixmap.isNull():
            pixmap_path = os.path.join(Icons.ICON_DIR, f"{name}.png")
            if os.path.exists(pixmap_path):
                pixmap = QPixmap(pixmap_path)
            else:
                # Return a blank pixmap rather than None to avoid crashes
                pixmap = QPixmap()
                
        return pixmap
