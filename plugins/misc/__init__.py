#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
CreepyAI Plugins Module
This module provides plugin functionality for CreepyAI
"""

import os
import sys
import logging
import importlib
import traceback
from typing import Dict, List, Any, Optional, Type

logger = logging.getLogger(__name__)

# Make sure plugins directory is in the Python path
PLUGINS_DIR = os.path.dirname(os.path.abspath(__file__))
if (PLUGINS_DIR not in sys.path):
    sys.path.insert(0, PLUGINS_DIR)

# Import core plugin classes
try:
    from .base_plugin import BasePlugin, LocationPoint
except ImportError as e:
    logger.error(f"Error importing base plugin classes: {e}")
    raise

# Set the version
__version__ = '1.0.0'

# Minimal set of required plugins - only import what's needed
try:
    from .DummyPlugin import DummyPlugin
    # Import more plugins as needed based on tree.txt
except ImportError as e:
    logger.warning(f"Could not import plugin: {e}")

def get_all_plugins():
    """
    Get all available plugins
    
    Returns:
        List of plugin instances
    """
    try:
        from plugins.plugins_manager import PluginsManager
        pm = PluginsManager()
        plugins = pm.load_all_plugins()
        return list(plugins.values())
    except ImportError as e:
        logger.warning(f"Could not import PluginsManager: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading plugins: {e}")
        logger.debug(traceback.format_exc())
        return []

def get_plugin_by_name(plugin_name):
    """
    Get a plugin by name
    
    Args:
        plugin_name: Name of the plugin to get
        
    Returns:
        Plugin instance or None if not found
    """
    try:
        from plugins.plugins_manager import PluginsManager
        pm = PluginsManager()
        for plugin_id, info in pm.discover_plugins().items():
            if info.get('name', '').lower() == plugin_name.lower() or plugin_id.lower() == plugin_name.lower():
                return pm.load_plugin(plugin_id)
        return None
    except ImportError:
        logger.warning("Could not import PluginsManager")
        return None
    except Exception as e:
        logger.error(f"Error getting plugin by name: {e}")
        logger.debug(traceback.format_exc())
        return None
