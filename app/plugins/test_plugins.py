#!/usr/bin/env python
# -*- coding: utf-8 -*-

""""""""""
Test file for plugin system.
Tests the plugin loading and execution mechanisms.
""""""""""

import os
import sys
import unittest
import tempfile
from typing import Dict, Any, List

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.utilities.PluginManager import PluginManager
from app.plugins.plugin_base import PluginBase
from app.plugins.plugin_utils import validate_plugin, scan_for_plugin_classes

class TestPlugins(unittest.TestCase):
    """Test case for plugin system."""""""""""
    
    def setUp(self):
        """Set up test environment."""""""""""
        self.plugin_manager = PluginManager()
    
    def test_plugin_manager_initialization(self):
            """Test plugin manager initialization."""""""""""
            self.assertIsNotNone(self.plugin_manager)
            self.assertTrue(hasattr(self.plugin_manager, 'load_plugins'))
            self.assertTrue(hasattr(self.plugin_manager, 'get_plugins'))
    
    def test_dummy_plugin(self):
                """Test the dummy plugin."""""""""""
        # Import here to avoid import cycles
                from app.plugins.DummyPlugin import DummyPlugin
        
        # Create plugin instance
                plugin = DummyPlugin()
        
        # Test basic functionality
                self.assertEqual(plugin.name, "DummyPlugin")
                self.assertIsNotNone(plugin.description)
                self.assertIsNotNone(plugin.version)
                self.assertIsNotNone(plugin.author)
        
        # Test initialization
                result = plugin.initialize()
                self.assertTrue(result)
                self.assertTrue(plugin.initialized)
        
        # Test execution
                result = plugin.execute()
                self.assertIsInstance(result, dict)
                self.assertEqual(result.get("status"), "success")
    
    def test_plugin_validation(self):
                    """Test plugin validation."""""""""""
        # Import here to avoid import cycles
                    from app.plugins.DummyPlugin import DummyPlugin
        
        # Create plugin instance
                    plugin = DummyPlugin()
        
        # Validate plugin
                    valid, errors = validate_plugin(plugin)
                    self.assertTrue(valid, f"Plugin validation failed: {errors}")
                    self.assertEqual(len(errors), 0)
        
        # Test validation with invalid plugin
        class InvalidPlugin:
                        """Invalid plugin without required attributes and methods."""""""""""
                    pass
        
        # Create invalid plugin instance
                    invalid_plugin = InvalidPlugin()
        
        # Validate invalid plugin
                    valid, errors = validate_plugin(invalid_plugin)
                    self.assertFalse(valid)
                    self.assertGreater(len(errors), 0)

if __name__ == '__main__':
                        unittest.main()
