"""
Compatibility layer for WebEngine functionality.
Ensures backward compatibility with older code using webengine_compat.
"""
import os
import sys
import logging

logger = logging.getLogger('creepyai.utilities.webengine_compat')

# Import and re-export from webengine
try:
    from .webengine import init_qt_webengine
except ImportError:
    logger.error("Failed to import webengine module")
    
    def init_qt_webengine():
        """Fallback implementation if webengine is not available."""
        logger.error("WebEngine initialization not available")
        return False

def initialize_webengine():
    """Initialize QtWebEngine (for backward compatibility)."""
    logger.info("Initializing WebEngine via compatibility layer")
    return init_qt_webengine()

def initialize_web_engine():
    """Alias for initialize_webengine to maintain backward compatibility."""
    logger.info("Calling initialize_web_engine (alias for initialize_webengine)")
    return initialize_webengine()

def set_qt_env_vars():
    """Set Qt environment variables (for backward compatibility)."""
    logger.info("Setting environment variables via compatibility layer")
    # This is now handled by init_qt_webengine
    return init_qt_webengine()

def check_webengine_availability():
    """
    Check if QtWebEngine is available for use.
    
    Returns:
        bool: True if QtWebEngine is available, False otherwise
    """
    logger.info("Checking WebEngine availability")
    try:
        from PyQt5 import QtWebEngineWidgets
        logger.info("QtWebEngine is available")
        return True
    except ImportError as e:
        logger.warning(f"QtWebEngine is not available: {e}")
        return False

# Make common functions available at module level for backward compatibility
if sys.platform == 'darwin':
    initialize_webengine()
