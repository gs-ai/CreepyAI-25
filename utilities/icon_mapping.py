#!/usr/bin/env python3
"""
Icon name mapping for CreepyAI.
Maps simple icon names to the actual filenames in the resources directory.
"""

# Dictionary mapping simple icon names to actual filenames (without .png extension)
ICON_MAPPING = {
    # Clear icons
    "clear": ['clear_all_16dp_000000', 'clear_all_24dp_000000'],

    # Close icons
    "close": ['close_16dp_000000', 'close_24dp_000000'],

    # Ddd icon
    "ddd": ['menu_24dp_000000'],

    # Download icon
    "download": ['file_download_24dp_000000'],

    # Editclear icons
    "editclear": ['edit_note_16dp_000000', 'edit_note_24dp_000000'],

    # Ellipse icon
    "ellipse": ['toggle_off_24dp_000000'],

    # Firewall icon
    "firewall": ['security_24dp_000000'],

    # Info icons
    "info": ['info_16dp_000000', 'info_24dp_000000'],

    # Location icon
    "location": ['location'],

    # Map icon
    "map": ['map_32dp_000000'],

    # Mapt icon
    "mapt": ['map_32dp_000000'],

    # Marker icons
    "marker": ['location-marker', 'map-marker', 'map_marker', 'marker', 'marker-icon', 'marker-shadow', 'marker_icon'],

    # Menu icon
    "menu": ['menu_24dp_000000'],

    # Minus icons
    "minus": ['remove_16dp_000000', 'remove_24dp_000000'],

    # Minus-circle icon
    "minus-circle": ['remove_circle_outline_24dp_000000'],

    # Open icon
    "open": ['open_in_new_24dp_000000'],

    # Pin icon
    "pin": ['pin'],

    # Play icon
    "play": ['play_arrow_24dp_000000'],

    # Plus icons
    "plus": ['add_16dp_000000', 'add_24dp_000000'],

    # Plus-circle icon
    "plus-circle": ['add_circle_outline_24dp_000000'],

    # Refresh icon
    "refresh": ['refresh_24dp_000000'],

    # Settings icons
    "settings": ['settings_24dp_000000', 'settings_32dp_000000'],

    # Toggle icon
    "toggle": ['toggle_off_24dp_000000'],

    # User icons
    "user": ['person_24dp_000000', 'person_32dp_000000'],
}

def get_icon_filename(simple_name, prefer_size=None):
    """
    Get the actual filename for a simple icon name.
    
    Args:
        simple_name: Simple name of the icon (e.g., 'user', 'plus')
        prefer_size: Preferred size ('16dp', '24dp', '32dp')
        
    Returns:
        The filename of the icon, or None if not found
    """
    if simple_name not in ICON_MAPPING:
        return None
        
    candidates = ICON_MAPPING[simple_name]
    
    # If a specific size is preferred, try to find it
    if prefer_size:
        for candidate in candidates:
            if prefer_size in candidate:
                return candidate + ".png"
    
    # Otherwise, return the first one (usually the larger/higher quality version)
    return candidates[0] + ".png"
