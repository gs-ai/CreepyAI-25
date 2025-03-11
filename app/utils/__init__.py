"""
Utilities for CreepyAI.
"""
import sys
import os
import logging

# Set up path for importing from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import src.utilities.PluginManager and make it available as utilities.PluginManager
try:
    from app.utilities.PluginManager import PluginManager
    # Create alias for backward compatibility
    sys.modules['utilities.PluginManager'] = sys.modules['src.utilities.PluginManager']
except ImportError as e:
    logging.getLogger('creepyai.utilities').error(f"Failed to import PluginManager: {e}")

# Add folium stub if folium is not installed
try:
    import folium
    logging.getLogger('creepyai.utilities').info("Found folium package")
except ImportError:
    from app.utilities.folium_stub import install_folium_stub
    install_folium_stub()
    logging.getLogger('creepyai.utilities').info("Installed folium stub")

# Import other utility modules
from .WebScrapingUtility import WebScrapingUtility, web_scraping_utility
from .GeocodingUtility import GeocodingUtility
from .GeneralUtilities import GeneralUtilities

__all__ = [
    'PluginManager', 
    'WebScrapingUtility',
    'GeocodingUtility',
    'GeneralUtilities',
    'web_scraping_utility'
]
