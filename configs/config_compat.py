"""
Configuration compatibility layer for CreepyAI.
Provides backward compatibility for code that references the old config path.
"""
import os
import sys
import warnings
import importlib
import logging
from typing import Optional, Dict, Any, Union

logger = logging.getLogger('creepyai.configs.compat')

# Get actual paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(CURRENT_DIR)
OLD_CONFIG_DIR = os.path.join(APP_ROOT, 'config')
NEW_CONFIG_DIR = CURRENT_DIR  # configs directory

def get_config_path(relative_path: str) -> str:
    """Get the correct config path, regardless of which directory it's in.
    
    Args:
        relative_path: Path relative to config directory
        
    Returns:
        Full path to the config file
    """
    # First try in new configs directory
    new_path = os.path.join(NEW_CONFIG_DIR, relative_path)
    if os.path.exists(new_path):
        return new_path
        
    # Then try old config directory
    old_path = os.path.join(OLD_CONFIG_DIR, relative_path)
    if os.path.exists(old_path):
        warnings.warn(
            f"Using file from old config path: {old_path}\n"
            f"Please migrate to new location: {new_path}",
            DeprecationWarning, stacklevel=2
        )
        return old_path
    
    # If not found in either, return the new path (even if it doesn't exist)
    return new_path

def import_config_module(module_name: str) -> Optional[Any]:
    """Import a module from either config directory.
    
    Args:
        module_name: Module name without the config/configs prefix
        
    Returns:
        Imported module or None if not found
    """
    try:
        # First try from new configs directory
        return importlib.import_module(f"configs.{module_name}")
    except ImportError:
        try:
            # Then try from old config directory
            module = importlib.import_module(f"config.{module_name}")
            warnings.warn(
                f"Using module from old config path: config.{module_name}\n"
                f"Please migrate to new location: configs.{module_name}",
                DeprecationWarning, stacklevel=2
            )
            return module
        except ImportError:
            logger.error(f"Could not import config module: {module_name}")
            return None

def get_settings_manager():
    """Get the settings manager instance from either directory."""
    settings_module = import_config_module('settings_manager')
    if settings_module:
        return settings_module.SettingsManager()
    return None
