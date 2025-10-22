"""Compatibility wrapper for legacy tooling imports.

This module re-exports everything from ``app.plugins.test_plugins`` so that
any code importing from ``app.plugins.tools`` continues to function
without maintaining duplicate implementations.
"""
from app.plugins.test_plugins import *  # noqa: F401,F403
import runpy as _runpy

if '__all__' not in globals():
    __all__ = [name for name in globals() if not name.startswith('_')]

if __name__ == '__main__':
    _runpy.run_module('app.plugins.test_plugins', run_name='__main__')
"""Unit tests covering the built-in plugin system."""

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
    """Test case for the plugin system."""

    def setUp(self):
        """Set up the plugin manager for each test."""
        self.plugin_manager = PluginManager()

    def test_plugin_manager_initialization(self):
        """The plugin manager exposes the expected API."""
        self.assertIsNotNone(self.plugin_manager)
        self.assertTrue(hasattr(self.plugin_manager, "load_plugins"))
        self.assertTrue(hasattr(self.plugin_manager, "get_plugins"))

    def test_dummy_plugin(self):
        """The dummy plugin implements the expected behaviour."""
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
        """Valid and invalid plugins are reported appropriately."""
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
            """Invalid plugin without required attributes and methods."""

            pass

        # Create invalid plugin instance
        invalid_plugin = InvalidPlugin()

        # Validate invalid plugin
        valid, errors = validate_plugin(invalid_plugin)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
