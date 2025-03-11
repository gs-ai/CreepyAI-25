"""
Assets package initialization.
Contains icons and other static resources needed by the application.
"""

import os

# Define the base asset directory path
ASSET_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(ASSET_DIR, 'icons')
MAP_ICONS_DIR = os.path.join(ICONS_DIR, 'map')
UI_ICONS_DIR = os.path.join(ICONS_DIR, 'ui')

def get_asset_path(relative_path):
    """
    Get the absolute path to an asset file.
    
    Args:
        relative_path: Path relative to the assets directory
        
    Returns:
        Absolute path to the asset
    """
    return os.path.join(ASSET_DIR, relative_path)

def get_icon_path(icon_name, icon_type='ui'):
    """
    Get the path to an icon file.
    
    Args:
        icon_name: Name of the icon file
        icon_type: Either 'ui' or 'map'
        
    Returns:
        Absolute path to the icon file
    """
    if icon_type.lower() == 'map':
        return os.path.join(MAP_ICONS_DIR, icon_name)
    else:
        return os.path.join(UI_ICONS_DIR, icon_name)
