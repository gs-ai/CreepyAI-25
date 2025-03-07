"""
Asset manager for handling access to icons and other static resources.
Provides a unified interface for the application to access assets.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, 'icons')
MAP_ICONS_DIR = os.path.join(ICONS_DIR, 'map')
UI_ICONS_DIR = os.path.join(ICONS_DIR, 'ui')

class AssetManager:
    """
    Manager for accessing application assets like icons.
    """
    
    @staticmethod
    def get_icon_path(icon_name, icon_type='ui'):
        """
        Get the path to an icon file.
        
        Args:
            icon_name: Name of the icon file (with or without extension)
            icon_type: Either 'ui' or 'map'
            
        Returns:
            Absolute path to the icon file or None if not found
        """
        if not icon_name.endswith('.png'):
            icon_name = f"{icon_name}.png"
        
        if icon_type.lower() == 'map':
            icon_path = os.path.join(MAP_ICONS_DIR, icon_name)
        else:
            icon_path = os.path.join(UI_ICONS_DIR, icon_name)
        
        if os.path.exists(icon_path):
            return icon_path
        else:
            logger.warning(f"Icon not found: {icon_path}")
            return None
    
    @staticmethod
    def list_icons(icon_type=None):
        """
        List all available icons.
        
        Args:
            icon_type: Optional filter ('ui', 'map', or None for all)
            
        Returns:
            List of icon filenames
        """
        icons = []
        
        if icon_type is None or icon_type.lower() == 'ui':
            ui_icons = [f for f in os.listdir(UI_ICONS_DIR) if f.endswith('.png')]
            icons.extend([('ui', icon) for icon in ui_icons])
        
        if icon_type is None or icon_type.lower() == 'map':
            map_icons = [f for f in os.listdir(MAP_ICONS_DIR) if f.endswith('.png')]
            icons.extend([('map', icon) for icon in map_icons])
        
        return icons

# Create a singleton instance
asset_manager = AssetManager()
