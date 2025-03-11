#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script to check and troubleshoot the plugin system
"""
import os
import sys
import logging
import importlib
import traceback
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure this script can import app modules
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def check_plugin_system():
    """Check if the plugin system is properly configured"""
    try:
        from app.core.plugins import PluginManager
        
        # Create plugin manager
        plugin_manager = PluginManager()
        
        # Discover plugins
        plugins = plugin_manager.discover_plugins()
        
        # Print summary
        print(f"\nDiscovered {len(plugins)} plugins")
        
        # Get plugins by category
        categories = plugin_manager.get_categories()
        
        for category in sorted(set(categories.values())):
            category_plugins = plugin_manager.get_plugins_by_category(category)
            print(f"\nCategory: {category.upper()} ({len(category_plugins)} plugins)")
            
            for name, plugin in sorted(category_plugins.items()):
                info = plugin.get_info() if hasattr(plugin, 'get_info') else {'name': name}
                print(f"  - {info.get('name', name)} (v{info.get('version', 'unknown')})")
        
        print("\nPlugin system check completed successfully.")
        
    except ImportError as e:
        logger.error(f"Failed to import plugin system: {e}")
        logger.error("Make sure the app module is in the Python path.")
    except Exception as e:
        logger.error(f"Error checking plugin system: {e}")
        logger.error(traceback.format_exc())

def check_specific_plugin(plugin_name):
    """Check a specific plugin by name"""
    try:
        from app.core.plugins import PluginManager
        
        # Create plugin manager
        plugin_manager = PluginManager()
        
        # Discover plugins
        plugin_manager.discover_plugins()
        
        # Try to get the specific plugin
        plugin = plugin_manager.get_plugin(plugin_name)
        
        if not plugin:
            print(f"Plugin '{plugin_name}' not found.")
            
            # List available plugins
            print("\nAvailable plugins:")
            for name in sorted(plugin_manager.plugins.keys()):
                print(f"  - {name}")
                
            return
        
        # Print plugin details
        print(f"\nPlugin: {plugin_name}")
        
        # Get information
        if hasattr(plugin, 'get_info'):
            info = plugin.get_info()
            print(f"Name: {info.get('name', 'Unknown')}")
            print(f"Description: {info.get('description', 'No description')}")
            print(f"Version: {info.get('version', 'Unknown')}")
            print(f"Author: {info.get('author', 'Unknown')}")
        
        # Check for essential methods
        print("\nMethods:")
        for method_name in ['run', 'configure', 'get_info']:
            if hasattr(plugin, method_name) and callable(getattr(plugin, method_name)):
                print(f"  - {method_name}: Available")
            else:
                print(f"  - {method_name}: Missing")
        
        # Check configuration if available
        if hasattr(plugin, 'is_configured'):
            try:
                configured, message = plugin.is_configured()
                print(f"\nConfiguration status: {'Configured' if configured else 'Not configured'}")
                print(f"Configuration message: {message}")
            except Exception as e:
                print(f"\nError checking configuration: {e}")
        
        print("\nPlugin check completed.")
        
    except ImportError as e:
        logger.error(f"Failed to import plugin system: {e}")
    except Exception as e:
        logger.error(f"Error checking plugin: {e}")
        logger.error(traceback.format_exc())

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Check specific plugin
        check_specific_plugin(sys.argv[1])
    else:
        # Check the entire plugin system
        check_plugin_system()
    
if __name__ == "__main__":
    main()
