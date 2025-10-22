#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test helper for manually validating individual plugins."""

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

def run_plugin_basics(plugin_class: type[PluginBase]) -> bool:
    """Run a set of basic checks against ``plugin_class``.

    Args:
        plugin_class: The plugin class to test.

    Returns:
        ``True`` if all checks pass, otherwise ``False``.
    """

    logger.info("Testing plugin class: %s", plugin_class.__name__)

    try:
        # Create instance
        plugin = plugin_class()

        # Check basic attributes
        assert hasattr(plugin, "name"), "Plugin missing 'name' attribute"
        assert hasattr(plugin, "description"), "Plugin missing 'description' attribute"
        assert hasattr(plugin, "version"), "Plugin missing 'version' attribute"
        assert hasattr(plugin, "author"), "Plugin missing 'author' attribute"

        # Check methods
        assert callable(getattr(plugin, "initialize", None)), "Plugin missing 'initialize' method"
        assert callable(getattr(plugin, "execute", None)), "Plugin missing 'execute' method"

        # Test initialize
        result = plugin.initialize()
        assert result is True, "Plugin initialization failed"
        assert plugin.initialized is True, "Plugin did not set initialized flag"

        logger.info(
            "Plugin %s v%s by %s passed basic tests",
            plugin.name,
            plugin.version,
            plugin.author,
        )
        return True
    except AssertionError as exc:
        logger.error("Plugin test failed: %s", exc)
        return False
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Unexpected error testing plugin: %s", exc)
        return False

if __name__ == "__main__":
    # Test DummyPlugin as an example
    run_plugin_basics(DummyPlugin)

    # Discover and test all plugins in this directory
    this_dir = os.path.dirname(__file__)
    plugin_classes = scan_for_plugin_classes(os.path.join(this_dir, "DummyPlugin.py"), PluginBase)

    for plugin_class in plugin_classes:
        run_plugin_basics(plugin_class)
