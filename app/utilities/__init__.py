"""
Utility functions for CreepyAI
"""
import sys
import logging
import os

logger = logging.getLogger('creepyai.utilities')

# Import and initialize webengine on macOS
if sys.platform == 'darwin':
    try:
        from .webengine import init_qt_webengine
        logger.info("WebEngine module imported and initialized")
    except ImportError as e:
        logger.error(f"Failed to import WebEngine module: {e}")

# Import PluginManager to ensure it's available
try:
    from .PluginManager import PluginManager
    logger.info("PluginManager imported successfully")
except ImportError as e:
    logger.error(f"Failed to import PluginManager: {e}")

# Add aliases for backward compatibility
try:
    # Import WebScrapingUtility from utilities package
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utilities.WebScrapingUtility import WebScrapingUtility
    # Make it available through the utilities module
    sys.modules['utilities.WebScrapingUtility'] = sys.modules['utilities.WebScrapingUtility']
except ImportError as e:
    logger.error(f"Failed to import WebScrapingUtility: {e}")
