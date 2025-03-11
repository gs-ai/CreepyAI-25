"""
UI icons package initialization.
Contains icons used in the UI components of the application.
"""

import os

UI_ICONS_DIR = os.path.dirname(os.path.abspath(__file__))

def get_ui_icon_path(icon_name):
    """
    Get the absolute path to a UI icon file.
    
    Args:
        icon_name: Name of the icon file
        
    Returns:
        Absolute path to the icon file
    """
    return os.path.join(UI_ICONS_DIR, icon_name)
