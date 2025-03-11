    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI Configuration Module

This module handles the application's configuration system, providing
centralized access to settings from various sources.
"""
import os
import sys
import logging
from pathlib import Path

# Import key configuration components
from .settings_manager import SettingsManager
from .defaults import DEFAULT_CONFIG

__version__ = '2.5.0'

# Set up module logger
logger = logging.getLogger('creepyai.config')

# Define important paths
_config_dir = Path(__file__).parent
APP_CONFIG_PATH = _config_dir / 'app' / 'app_config.json'
LOGGING_CONFIG_PATH = _config_dir / 'logging' / 'logging_config.json'
PLUGINS_CONFIG_DIR = _config_dir / 'plugins'
KML_TEMPLATE_PATH = _config_dir / 'app' / 'kml_template.xml'

# Create settings manager instance for module-level access
settings_manager = SettingsManager()

# Initialize settings from defaults
settings_manager.load_defaults(DEFAULT_CONFIG)

# Load from app config if it exists
if APP_CONFIG_PATH.exists():
    settings_manager.load_from_file(APP_CONFIG_PATH)

def get_setting(key, default=None):
    """
    Get a configuration setting by key with dotted path notation
    
    Args:
        key (str): The setting key with dot notation (e.g., 'app.debug')
        default: Default value if key not found
        
    Returns:
        The setting value or the default if not found
    """
    return settings_manager.get(key, default)

def set_setting(key, value):
    """
    Set a configuration setting
    
    Args:
        key (str): The setting key with dot notation
        value: The value to set
    """
    settings_manager.set(key, value)

def save_settings(path=None):
    """Save current settings to file"""
    return settings_manager.save(path)

def reset_to_defaults():
    """Reset settings to default values"""
    settings_manager.load_defaults(DEFAULT_CONFIG)
