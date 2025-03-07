"""
CreepyAI - A geospatial intelligence gathering framework

This package provides tools for gathering and analyzing location-based data
from various online sources through a plugin architecture.
"""

import logging
import importlib
import sys

# Configure package-level logger
logger = logging.getLogger(__name__)

# Package metadata
__version__ = "0.1.0"
__author__ = "CreepyAI Development Team"

# Initialize resources
try:
    import creepy.creepy_resources_rc as creepy_resources_rc
    logger.debug("Resource module successfully imported")
except ImportError:
    logger.warning(
        "Could not import resource module (creepy_resources_rc). "
        "Some UI elements may not display correctly. "
        "Run 'python build_resources.py' to generate the resource module."
    )

# Import key modules for easier access
def _import_optional_module(module_name):
    """Helper function to import optional modules without breaking if not available."""
    try:
        return importlib.import_module(f".{module_name}", package="CreepyAI")
    except ImportError as e:
        logger.debug(f"Optional module '{module_name}' not available: {e}")
        return None

# Make key components available at package level
settings_manager = _import_optional_module("settings_manager")
factory = _import_optional_module("factory")

# Initialize UI if in GUI mode
def is_gui_mode():
    """Check if application is running in GUI mode."""
    # Simple check - no command line arguments usually means GUI mode
    # This could be enhanced with more sophisticated detection
    return len(sys.argv) <= 1

# Setup for GUI if needed
if is_gui_mode():
    try:
        # PyQt5 is required for GUI operation
        from PyQt5 import QtWidgets
        logger.debug("GUI mode detected, PyQt5 available")
    except ImportError:
        logger.warning(
            "GUI mode detected but PyQt5 is not available. "
            "Install PyQt5 to use the graphical interface: pip install PyQt5"
        )

def get_version():
    """Return the current version of CreepyAI."""
    return __version__

def setup_logging(level=logging.INFO):
    """
    Configure logging for CreepyAI.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            # Uncomment to add file logging
            # logging.FileHandler("creepy.log")
        ]
    )
    logger.debug(f"Logging initialized at level: {logging.getLevelName(level)}")
