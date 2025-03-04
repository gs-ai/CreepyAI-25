#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
import argparse

# Add project root to path
app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_path)

# Import core components
from core.logger import setup_logger
from core.config_manager import ConfigManager

# Import plugin system components
try:
    from yapsy.PluginManager import PluginManagerSingleton
    from creepy.models.InputPlugin import InputPlugin
except ImportError as e:
    if "yapsy" in str(e):
        print("Error: The yapsy plugin system is required.")
        print("Please install it with: pip install yapsy")
    elif "InputPlugin" in str(e):
        print("Error: Could not import InputPlugin class from creepy.models.")
        print("Make sure the project structure is intact.")
    else:
        print(f"Error importing plugin system components: {e}")
    sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Test CreepyAI plugins')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-c', '--config', help='Path to config file')
    parser.add_argument('-p', '--plugin', help='Test specific plugin (or all if not specified)')
    return parser.parse_args()

def discover_plugins(plugin_path):
    """
    Discover available plugins using yapsy plugin manager
    """
    logger = logging.getLogger('creepy')
    logger.info(f"Discovering plugins in {plugin_path}")
    
    # Clear any existing singleton instances
    if hasattr(PluginManagerSingleton, '_PluginManagerSingleton__instance'):
        PluginManagerSingleton._PluginManagerSingleton__instance = None
    
    # Initialize plugin manager
    plugin_manager = PluginManagerSingleton.get()
    plugin_manager.setCategoriesFilter({'Input': InputPlugin})
    
    # Set plugin directory - check both the creepy/plugins path and the plugins path at project root
    plugin_paths = [
        plugin_path,  # The path from config (creepy/plugins)
        os.path.join(app_path, 'plugins')  # The path used in core/main.py
    ]
    
    plugin_paths = [p for p in plugin_paths if os.path.exists(p)]
    if not plugin_paths:
        logger.error(f"No valid plugin directories found")
        return []
    
    logger.info(f"Looking for plugins in: {', '.join(plugin_paths)}")
    plugin_manager.setPluginPlaces(plugin_paths)
    
    # Check if plugin files have .yapsy-plugin extension files
    # If not, create temporary ones for testing
    create_temp_plugin_files(plugin_paths)
    
    logger.info("Locating plugins...")
    plugin_manager.locatePlugins()
    
    logger.info("Loading plugins...")
    plugin_manager.loadPlugins()
    
    # Get all loaded plugins
    plugins = plugin_manager.getAllPlugins()
    plugin_names = [plugin.name for plugin in plugins]
    logger.info(f"Plugin names: {', '.join(plugin_names) if plugin_names else 'None'}")
    
    return plugins

def create_temp_plugin_files(plugin_paths):
    """
    Create temporary .yapsy-plugin files for Python modules that appear to be plugins
    This helps yapsy discover plugins that don't have explicit metadata files
    """
    logger = logging.getLogger('creepy')
    temp_files_created = []
    
    for plugin_dir in plugin_paths:
        if not os.path.exists(plugin_dir):
            continue
            
        for filename in os.listdir(plugin_dir):
            if filename.endswith('_plugin.py'):
                plugin_name = filename[:-3]  # Remove .py
                module_path = os.path.join(plugin_dir, filename)
                yapsy_file_path = os.path.join(plugin_dir, f"{plugin_name}.yapsy-plugin")
                
                # Only create if yapsy file doesn't exist
                if not os.path.exists(yapsy_file_path):
                    with open(yapsy_file_path, 'w') as f:
                        f.write(f"""[Core]
Name = {plugin_name.replace('_', ' ').title()}
Module = {plugin_name}

[Documentation]
Description = Auto-generated plugin metadata for testing
Author = CreepyAI Testing Framework
Version = 1.0.0
Website = https://example.com
""")
                    temp_files_created.append(yapsy_file_path)
    
    if temp_files_created:
        logger.info(f"Created {len(temp_files_created)} temporary plugin metadata files")

def cleanup_temp_files(plugin_paths):
    """Remove temporary .yapsy-plugin files created for testing"""
    for plugin_dir in plugin_paths:
        if not os.path.exists(plugin_dir):
            continue
            
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.yapsy-plugin'):
                # Only remove files we created (simple check - could be improved)
                yapsy_path = os.path.join(plugin_dir, filename)
                with open(yapsy_path) as f:
                    content = f.read()
                    if "Auto-generated plugin metadata for testing" in content:
                        os.remove(yapsy_path)

def test_plugin(plugin, config_manager):
    """
    Test a single plugin's functionality using the yapsy plugin system
    """
    logger = logging.getLogger('creepy')
    logger.info(f"Testing plugin: {plugin.name}")
    
    result = {
        'name': plugin.name,
        'loaded': True,  # Already loaded by yapsy
        'functions_tested': 0,
        'functions_passed': 0,
        'errors': []
    }
    
    try:
        # Test plugin configuration
        if hasattr(plugin, 'is_configured'):
            config_status = plugin.is_configured()
            result['functions_tested'] += 1
            if config_status[0]:
                result['functions_passed'] += 1
            else:
                result['errors'].append(f"Configuration issue: {config_status[1]}")
        
        # Test activation
        if hasattr(plugin, 'activate'):
            plugin.activate()
            result['functions_tested'] += 1
            result['functions_passed'] += 1
        
        # Test basic plugin functionality
        # Add more tests based on your plugin API
        
    except Exception as e:
        result['errors'].append(str(e))
    
    return result

import logging
from utilities.PluginManager import PluginManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting CreepyAI plugin tests...")
    
    plugin_manager = PluginManager()
    plugin_manager.load_plugins()
    
    # Example of initializing a specific plugin
    plugin_manager.initialize_plugin('example_plugin')
    
    # Count loaded plugins
    plugins = plugin_manager.get_all_plugins()
    logger.info(f"Loaded {len(plugins)} plugins")
    
    # Check for plugin configuration issues
    config_issues = []
    for plugin in plugins:
        try:
            config_status = plugin.is_configured()
            if not config_status[0]:
                config_issues.append(f"{plugin.name}: {config_status[1]}")
        except Exception as e:
            config_issues.append(f"{plugin.name}: Error checking configuration - {str(e)}")
    
    if config_issues:
        logger.warning(f"Found {len(config_issues)} plugin configuration issues:")
        for issue in config_issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("All plugins are properly configured")

if __name__ == "__main__":
    main()
