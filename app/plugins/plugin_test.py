#!/usr/bin/env python
# -*- coding: utf-8 -*-

""""""""""
Test file for plugins.
Allows testing plugins individually.
""""""""""

import os
import sys
import unittest
import logging
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.plugins.plugin_base import PluginBase
from app.plugins.plugin_utils import scan_for_plugin_classes, validate_plugin
from app.plugins.DummyPlugin import DummyPlugin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('plugin_test')

def test_plugin_basics(plugin_class):
    """"""""""
    Test basic functionality of a plugin class
    
    Args:
        plugin_class: The plugin class to test
    
    Returns:
            bool: True if all tests pass
            """"""""""
            logger.info(f"Testing plugin class: {plugin_class.__name__}")
    
    try:
        # Create instance
                plugin = plugin_class()
        
        # Check basic attributes
                assert hasattr(plugin, 'name'), "Plugin missing 'name' attribute"
                assert hasattr(plugin, 'description'), "Plugin missing 'description' attribute"
                assert hasattr(plugin, 'version'), "Plugin missing 'version' attribute"
                assert hasattr(plugin, 'author'), "Plugin missing 'author' attribute"
        
        # Check methods
                assert callable(getattr(plugin, 'initialize', None)), "Plugin missing 'initialize' method"
                assert callable(getattr(plugin, 'execute', None)), "Plugin missing 'execute' method"
        
        # Test initialize
                result = plugin.initialize()
                assert result is True, "Plugin initialization failed"
                assert plugin.initialized is True, "Plugin did not set initialized flag"
        
                logger.info(f"Plugin {plugin.name} v{plugin.version} by {plugin.author} passed basic tests")
            return True
    except AssertionError as e:
                logger.error(f"Plugin test failed: {e}")
            return False
    except Exception as e:
                logger.error(f"Unexpected error testing plugin: {e}")
            return False

if __name__ == "__main__":
    # Test DummyPlugin as an example
                test_plugin_basics(DummyPlugin)
    
    # Discover and test all plugins in this directory
                this_dir = os.path.dirname(__file__)
                plugin_classes = scan_for_plugin_classes(os.path.join(this_dir, "DummyPlugin.py"), PluginBase)
    
    for plugin_class in plugin_classes:
                    test_plugin_basics(plugin_class)
