    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Icon management for CreepyAI application.
"""

import os
import logging
from PyQt5.QtGui import QIcon, QPixmap

logger = logging.getLogger(__name__)

class Icons:
    """
    Handles loading and providing icons for the application.
    Uses material design icons from the resources directory.
    """
    
    _icons_cache = {}  # Cache to avoid reloading icons
    _resources_path = os.path.dirname(os.path.abspath(__file__))
    
    @classmethod
    def get_icon(cls, name):
        """
        Get an icon by name.
        
        Args:
            name: Icon name without extension
            
        Returns:
            QIcon object or a default icon if not found
        """
        if name in cls._icons_cache:
            return cls._icons_cache[name]
        
        # Map icon names to actual filenames
        icon_map = {
            # Common UI icons
            "new_project": "add_24dp_000000",
            "open_project": "folder_open_24dp_000000",  
            "save_project": "save_24dp_000000",
            "analyze": "analytics_24dp_000000",
            "export": "export_24dp_000000",
            "filter_date": "date_range_24dp_000000",
            "filter_location": "place_24dp_000000",
            "clear_filters": "clear_24dp_000000",
            
            # Map icons
            "zoom_in": "add_24dp_000000",
            "zoom_out": "remove_24dp_000000",
            "map": "map_32dp_000000",
            "person": "person_24dp_000000",
            
            # Fallback to default application icon
            "app": "app_icon"
        }
        
        # Get filename from map or use name directly
        filename = icon_map.get(name, name)
        icon_path = os.path.join(cls._resources_path, f"{filename}.png")
        
        # Try to load the icon
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            cls._icons_cache[name] = icon
            return icon
        
        # If icon doesn't exist, use default app icon or create an empty icon
        logger.warning(f"Icon not found: {name} (tried {icon_path})")
        
        # Use app icon as fallback if available
        app_icon_path = os.path.join(cls._resources_path, "app_icon.png")
        if os.path.exists(app_icon_path):
            icon = QIcon(app_icon_path)
        else:
            # Create an empty icon as last resort
            icon = QIcon()
            
        cls._icons_cache[name] = icon
        return icon
