#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test script for the CreepyAI plugin system.
This script demonstrates plugin discovery, loading, and execution.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # Updated to point to parent directory
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    """Main test function"""
    logger.info("Testing CreepyAI Plugin System")
    
    try:
        # Install dependencies if missing
        try:
            import yaml
        except ImportError:
            logger.info("Installing missing dependency: pyyaml")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
            import yaml
            
        try:
            import psutil
        except ImportError:
            logger.info("Installing missing dependency: psutil")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
            
        # Import the plugins manager
        from plugins.plugins_manager import PluginsManager
        
        # Create plugin manager
        plugin_manager = PluginsManager()
        
        # Discover plugins
        logger.info("Discovering plugins...")
        plugins = plugin_manager.discover_plugins()
        logger.info(f"Found {len(plugins)} plugins:")
        for plugin_id, info in plugins.items():
            logger.info(f"  - {plugin_id}: {info.get('name', plugin_id)}")
        
        # Test DummyPlugin
        logger.info("\nTesting DummyPlugin...")
        dummy_plugin = plugin_manager.load_plugin("DummyPlugin")
        if dummy_plugin:
            logger.info(f"  Loaded DummyPlugin: {dummy_plugin.name} (v{dummy_plugin.get_version()})")
            
            # Check configuration
            configured, message = dummy_plugin.is_configured()
            logger.info(f"  Is configured: {configured} - {message}")
            
            # Generate locations
            locations = dummy_plugin.collect_locations("test")
            logger.info(f"  Generated locations: {locations}")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
