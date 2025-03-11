"""
Plugin icon utilities for CreepyAI
"""
import os
from PyQt5.QtGui import QIcon

# Base directory for plugin icons
ICON_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_CATEGORIES = {
    'social_media': 'social_media.png',
    'location_services': 'location.png',
    'data_extraction': 'data.png',
    'tools': 'tool.png',
    'standard': 'standard.png',
    'other': 'plugin.png',
    'uncategorized': 'plugin.png'
}

def get_plugin_icon(plugin_name, category):
    """
    Get an appropriate icon for a plugin based on its name and category
    
    Args:
        plugin_name: Name of the plugin
        category: Plugin category
        
    Returns:
        QIcon: Icon for the plugin
    """
    # Try to find a plugin-specific icon first
    plugin_icon_path = os.path.join(ICON_DIR, f"plugin_{plugin_name.lower()}.png")
    if os.path.exists(plugin_icon_path):
        return QIcon(plugin_icon_path)
    
    # Fall back to category icon
    if category in ICON_CATEGORIES:
        category_icon_path = os.path.join(ICON_DIR, ICON_CATEGORIES[category])
        if os.path.exists(category_icon_path):
            return QIcon(category_icon_path)
    
    # Default plugin icon
    default_icon_path = os.path.join(ICON_DIR, 'plugin.png')
    if os.path.exists(default_icon_path):
        return QIcon(default_icon_path)
    
    # No icons found, return empty icon
    return QIcon()
