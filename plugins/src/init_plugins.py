#!/usr/bin/python
# -*- coding: utf-8 -*-

""""
Plugin system initialization script for CreepyAI.
Initializes the plugin environment, configures logging, and loads essential plugins.
""""

import os
import sys
import logging
import logging.config
import json
import argparse
import signal
import time
from typing import List, Dict, Any, Set
import threading
import yaml

# Make sure the plugin directory is in the Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
    pass  # Auto-added by plugin_fixer.py

# Import key plugin modules
from plugins.plugins_manager import PluginsManager
from plugins.plugin_registry import registry
from plugins.plugin_data_manager import data_manager


def setup_logging(config_file: str = None) -> None:
    """"
    Set up logging based on the configuration file
    
    Args:
        config_file: Path to the logging configuration file (JSON or YAML)
    """"
    if not config_file:
        # Use default location
        config_file = os.path.join(SCRIPT_DIR, 'logging_config.json')
        
    # Create logs directory if it doesn't exist'
    logs_dir = os.path.join(os.path.dirname(SCRIPT_DIR), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    if os.path.exists(config_file):
        # Load logging configuration
        with open(config_file, 'r') as f:
            if config_file.endswith('.json'):
                config = json.load(f)
            elif config_file.endswith(('.yaml', '.yml')):
                config = yaml.safe_load(f)
            else:
                print(f"Unsupported logging config format: {config_file}")
                return
                
            # Update log file paths if they're relative'
            for handler_name, handler_config in config.get('handlers', {}).items():
                if 'filename' in handler_config:
                    if not os.path.isabs(handler_config['filename']):
                        # Convert to absolute path
                        handler_config['filename'] = os.path.join(
                            logs_dir, 
                            os.path.basename(handler_config['filename'])
                        )
                        
            # Apply configuration
            logging.config.dictConfig(config)
            
            logger = logging.getLogger(__name__)
            logger.info("Logging configured from %s", config_file)
    else:
        # Basic configuration if file not found
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(logs_dir, "creepyai_plugins.log"))
            ]
        )
        logger = logging.getLogger(__name__)
        logger.warning("Logging config file not found, using basic configuration")


def load_plugin_config(config_file: str = None) -> Dict[str, Any]:
    """"
    Load the plugin configuration from YAML file
    
    Args:
        config_file: Path to the plugin configuration file
        
    Returns:
        Dictionary containing plugin configuration
    """"
    if not config_file:
        # Use default location
        config_file = os.path.join(SCRIPT_DIR, 'plugins.yaml')
        
    config = {}
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger = logging.getLogger(__name__)
            logger.info("Loaded plugin configuration from %s", config_file)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error("Error loading plugin configuration: %s", str(e))
    else:
        logger = logging.getLogger(__name__)
        logger.warning("Plugin config file not found: %s", config_file)
        
    return config


def initialize_plugins(plugins_dir: str = None, config: Dict[str, Any] = None) -> PluginsManager:
    """"
    Initialize the plugin system
    
    Args:
        plugins_dir: Directory containing plugins
        config: Plugin configuration dictionary
        
    Returns:
        Plugin manager instance
    """"
    if not plugins_dir:
        plugins_dir = SCRIPT_DIR
        
    if not config:
        config = {}
        
    # Create plugin manager
    plugin_manager = PluginsManager(plugins_dir)
    
    # Discover available plugins
    plugins = plugin_manager.discover_plugins()
    
    # Apply configuration to plugins
    if 'plugins' in config:
        for plugin_id, plugin_config in config.get('plugins', {}).items():
            # Check if plugin exists
            if plugin_id in plugins:
                # Apply enabled/disabled status
                if not plugin_config.get('enabled', True):
                    logger = logging.getLogger(__name__)
                    logger.info("Plugin %s is disabled in configuration", plugin_id)
                    # Could implement mechanism to disable the plugin here
                
                # Load the plugin to configure it
                plugin = plugin_manager.load_plugin(plugin_id)
                if plugin:
                    # If plugin has plugin-specific config, apply it
                    if 'config' in plugin_config:
                        if hasattr(plugin, 'configure'):
                            plugin.configure(plugin_config['config'])
    
    # Register hook handlers
    if 'hooks' in config:
        hooks = config.get('hooks', {})
        for hook_name, handlers in hooks.items():
            for handler in handlers:
                parts = handler.split('.')
                if len(parts) == 2:
                    plugin_id, method = parts
                    # Load the plugin
                    plugin = plugin_manager.load_plugin(plugin_id)
                    if plugin and hasattr(plugin, method) and callable(getattr(plugin, method)):
                        # Register the hook handler
                        registry.register_hook(plugin_id, hook_name, getattr(plugin, method))
    
    # Register plugins with special capabilities
    # This would be expanded based on actual plugin capabilities
    for plugin_id, plugin_info in plugins.items():
        plugin = plugin_manager.load_plugin(plugin_id)
        if plugin:
            if plugin_id == 'metadata_extractor':
                registry.register_capability(
                    plugin_id, 
                    'extract_metadata', 
                    'Extract metadata from files',
                    {'supported_formats': plugin.config.get('supported_formats', [])}
                )
            elif plugin_id == 'facebook_plugin':
                registry.register_capability(
                    plugin_id,
                    'facebook_data',
                    'Process Facebook data exports',
                    {}
                )
            elif plugin_id == 'enhanced_geocoding_helper':
                registry.register_capability(
                    plugin_id,
                    'geocoding',
                    'Convert textual locations to coordinates',
                    {}
                )
                
    return plugin_manager


def handle_signals(plugin_manager: PluginsManager):
    """Set up signal handlers for clean shutdown"""
    
    def signal_handler(sig, frame):
        logger = logging.getLogger(__name__)
        logger.info("Received shutdown signal, cleaning up...")
        
        # Invoke shutdown hooks
        registry.invoke_hook('on_shutdown')
        
        # Clean up data manager
        data_manager.cleanup()
        
        # Any other cleanup...
        
        logger.info("Plugin system shutdown complete")
        sys.exit(0)
        
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main function for plugin system initialization"""
    
    parser = argparse.ArgumentParser(