"""
Icons package initialization.
Contains map and UI icons for the application.
"""

import os

# Define base paths
ICONS_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_ICONS_DIR = os.path.join(ICONS_DIR, 'map')
UI_ICONS_DIR = os.path.join(ICONS_DIR, 'ui')

# Create mapping of common icon names to filenames
ICON_MAPPING = {
    'add': 'add_24dp_000000.png',
    'add_small': 'add_16dp_000000.png',
    'settings': 'settings_24dp_000000.png',
    'settings_large': 'settings_32dp_000000.png',
    'person': 'person_24dp_000000.png',
    'person_large': 'person_32dp_000000.png',
    'close': 'close_24dp_000000.png',
    'close_small': 'close_16dp_000000.png',
    'download': 'file_download_24dp_000000.png',
    'refresh': 'refresh_24dp_000000.png',
    'app': 'app_icon.png',
    'remove': 'remove_24dp_000000.png',
    'location_marker': 'location-marker.png',
    'marker_shadow': 'marker-shadow.png',
}

def get_icon_path(icon_name, icon_type='ui'):
    """
    Get the path to an icon by name.
    
    Args:
        icon_name: Either the direct filename or a common icon name from ICON_MAPPING
        icon_type: Either 'ui' or 'map'
        
    Returns:
        Absolute path to the icon file
    """
    # If it's a known icon name, get the actual filename
    filename = ICON_MAPPING.get(icon_name, icon_name)
    
    # Determine the correct directory
    if icon_type.lower() == 'map':
        return os.path.join(MAP_ICONS_DIR, filename)
    else:
        return os.path.join(UI_ICONS_DIR, filename)
