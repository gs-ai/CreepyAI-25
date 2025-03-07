"""
Icons module for CreepyAI

This module provides access to application icons using either PyQt5 or standard paths.
"""
import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Icons:
    """
    Icons class for managing application icons
    
    Provides access to application icons with PyQt5 support if available,
    otherwise falls back to direct file paths.
    """
    
    # Base resource paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
    
    # Icon mapping (name -> filename)
    ICON_MAP = {
        'app': 'app_icon.png',
        'add': 'add_24dp_000000.png',
        'add_small': 'add_16dp_000000.png',
        'add_circle': 'add_circle_outline_24dp_000000.png',
        'analytics': 'analytics_24dp_000000.png',
        'clear': 'clear_24dp_000000.png',
        'clear_all': 'clear_all_24dp_000000.png',
        'clear_all_small': 'clear_all_16dp_000000.png',
        'close': 'close_24dp_000000.png',
        'close_small': 'close_16dp_000000.png',
        'date': 'date_range_24dp_000000.png',
        'edit': 'edit_note_24dp_000000.png',
        'edit_small': 'edit_note_16dp_000000.png',
        'export': 'export_24dp_000000.png',
        'download': 'file_download_24dp_000000.png',
        'folder': 'folder_open_24dp_000000.png',
        'info': 'info_24dp_000000.png',
        'info_small': 'info_16dp_000000.png',
        'location_marker': 'location-marker.png',
        'location': 'location.png',
        'map_marker': 'map-marker.png',
        'map': 'map_32dp_000000.png',
        'marker': 'marker.png',
        'marker_icon': 'marker-icon.png',
        'marker_shadow': 'marker-shadow.png',
        'menu': 'menu_24dp_000000.png',
        'open_new': 'open_in_new_24dp_000000.png',
        'person': 'person_24dp_000000.png',
        'person_large': 'person_32dp_000000.png',
        'pin': 'pin.png',
        'place': 'place_24dp_000000.png',
        'play': 'play_arrow_24dp_000000.png',
        'refresh': 'refresh_24dp_000000.png',
        'remove': 'remove_24dp_000000.png',
        'remove_small': 'remove_16dp_000000.png',
        'remove_circle': 'remove_circle_outline_24dp_000000.png',
        'save': 'save_24dp_000000.png',
        'security': 'security_24dp_000000.png',
        'settings': 'settings_24dp_000000.png',
        'settings_large': 'settings_32dp_000000.png',
        'toggle_off': 'toggle_off_24dp_000000.png',
    }
    
    # Initialize PyQt support
    try:
        from PyQt5.QtGui import QIcon, QPixmap
        from PyQt5.QtCore import QFile, QIODevice
        HAS_PYQT = True
    except ImportError:
        HAS_PYQT = False
    
    @classmethod
    def get_icon(cls, name):
        """
        Get an icon by name
        
        Args:
            name: Icon name from ICON_MAP
            
        Returns:
            PyQt5 QIcon if PyQt5 is available, otherwise file path as string
        """
        if name not in cls.ICON_MAP:
            logger.warning(f"Icon '{name}' not found in icon map")
            return None
            
        icon_file = cls.ICON_MAP[name]
        
        if cls.HAS_PYQT:
            try:
                from PyQt5.QtGui import QIcon, QPixmap
                # Try to load from resource file first
                icon = QIcon(f":/creepy/{name}")
                if not icon.isNull():
                    return icon
                    
                # Fall back to file path
                icon_path = os.path.join(cls.RESOURCES_DIR, icon_file)
                if os.path.exists(icon_path):
                    return QIcon(icon_path)
            except Exception as e:
                logger.error(f"Error loading icon {name}: {e}")
                
        # Return file path as fallback or for non-PyQt environments
        return os.path.join(cls.RESOURCES_DIR, icon_file)
    
    @classmethod
    def get_path(cls, name):
        """
        Get the file path for an icon
        
        Args:
            name: Icon name from ICON_MAP
            
        Returns:
            Path to the icon file as string
        """
        if name not in cls.ICON_MAP:
            logger.warning(f"Icon '{name}' not found in icon map")
            return None
            
        return os.path.join(cls.RESOURCES_DIR, cls.ICON_MAP[name])
