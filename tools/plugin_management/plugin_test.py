#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for plugin system
This script directly tests the plugin system without the GUI
"""

import os
import sys
import logging
from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("PluginTest")

def main():
    logger.info("Starting plugin test")
    
    # Ensure paths are correctly set
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Initialize plugin manager
    logger.info("Initializing plugin manager")
    plugin_manager = PluginManagerSingleton.get()
    plugin_manager.setCategoriesFilter({'Input': InputPlugin})
    plugin_manager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
    plugin_manager.locatePlugins()
    plugin_manager.loadPlugins()
    
    # List all discovered plugins
    logger.info("Discovered plugins:")
    for plugin in plugin_manager.getAllPlugins():
        logger.info(f"  - {plugin.name} ({plugin.path})")
    
    # Test searchForTargets with dummy plugin
    dummy_plugin = plugin_manager.getPluginByName("DummyPlugin", "Input")
    if dummy_plugin:
        logger.info("Testing searchForTargets with DummyPlugin")
        targets = dummy_plugin.plugin_object.searchForTargets("test_search")
        logger.info(f"Returned targets: {targets}")
        
        if targets:
            # Test returnLocations
            logger.info("Testing returnLocations with first target")
            locations = dummy_plugin.plugin_object.returnLocations(targets[0], {})
            logger.info(f"Returned {len(locations)} locations")
            if locations:
                logger.info(f"First location: {locations[0]}")
    else:
        logger.error("DummyPlugin not found")
    
    logger.info("Plugin test complete")

if __name__ == "__main__":
    main()
