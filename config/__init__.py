#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration package for CreepyAI.
Provides access to application configuration, plugin settings, and logging configuration.
"""

import os
import json
import sys
from typing import Dict, Any, Optional
import logging

# Define paths to config directories
CONFIG_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_CONFIG_DIR = os.path.join(CONFIG_ROOT, 'app')
LOGGING_CONFIG_DIR = os.path.join(CONFIG_ROOT, 'logging')
PLUGINS_CONFIG_DIR = os.path.join(CONFIG_ROOT, 'plugins')

# Ensure all required subdirectories exist
for dir_path in [APP_CONFIG_DIR, LOGGING_CONFIG_DIR, PLUGINS_CONFIG_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Import key functionality
from .settings_manager import SettingsManager

# Create default settings manager instance
settings_manager = SettingsManager()

# Default configurations
from .defaults import default_app_config, default_logging_config

# Initialize logger
logger = logging.getLogger(__name__)

def _load_json_config(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load a JSON configuration file
    
    Args:
        filepath: Path to JSON configuration file
        
    Returns:
        Configuration dictionary or None if loading fails
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading config from {filepath}: {e}")
        return None

# Try to load configuration from files
config_dir = os.path.dirname(os.path.abspath(__file__))

# App configuration
app_config_path = os.path.join(config_dir, 'app_config.json')
app_config = _load_json_config(app_config_path) or default_app_config

# Logging configuration
logging_config_path = os.path.join(config_dir, 'logging_config.json')
logging_config = _load_json_config(logging_config_path) or default_logging_config

def get_logging_config() -> Dict[str, Any]:
    """Get the current logging configuration"""
    return logging_config

def get_app_config() -> Dict[str, Any]:
    """Get the current application configuration"""
    return app_config

def save_app_config(new_config: Dict[str, Any]) -> bool:
    """
    Save updated application configuration to file
    
    Args:
        new_config: New configuration dictionary
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with open(app_config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        # Update the global config
        global app_config
        app_config = new_config
        
        logger.info("App configuration saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving app configuration: {e}")
        return False

def get_app_config_path(filename='app_config.json'):
    """Get the path to an app configuration file"""
    return os.path.join(APP_CONFIG_DIR, filename)

def get_logging_config_path(filename='logging_config.json'):
    """Get the path to a logging configuration file"""
    return os.path.join(LOGGING_CONFIG_DIR, filename)

def get_plugin_config_path(plugin_name):
    """Get the path to a plugin configuration file"""
    return os.path.join(PLUGINS_CONFIG_DIR, f"{plugin_name}.conf")

def get_plugins_yaml_path():
    """Get the path to the plugins.yaml file"""
    return os.path.join(PLUGINS_CONFIG_DIR, "plugins.yaml")

# Export the settings manager instance
__all__ = ['settings_manager', 'get_app_config_path', 'get_logging_config_path', 
           'get_plugin_config_path', 'get_plugins_yaml_path']
