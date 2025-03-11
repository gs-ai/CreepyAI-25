"""
Core include package for CreepyAI
Contains shared utilities and constants used throughout the application
"""

import logging
import os

# Set up module logger
logger = logging.getLogger('creepyai.core.include')

# Import all components to make them available through the include package
try:
    from .constants import *
    from .config_manager import ConfigManager
    from .logger_setup import configure_logger
    from .platform_utils import get_platform_info, is_macos, is_windows, is_linux

    logger.debug("Core include package initialization complete")
except ImportError as e:
    logger.error(f"Error importing core include components: {e}")

__all__ = [
    'ConfigManager',
    'configure_logger',
    'get_platform_info',
    'is_macos',
    'is_windows', 
    'is_linux'
]
