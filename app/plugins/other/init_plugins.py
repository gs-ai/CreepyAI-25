#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin system initialization script for CreepyAI.
"""
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

logger = logging.getLogger(__name__)

class Plugin:
    """Plugin initialization tool"""
    
    def __init__(self):
        self.name = "Plugin Initializer"
        self.description = "Initialize and setup plugin system"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        self.config_file = os.path.join(os.path.expanduser("~"), ".creepyai", "config", "plugins.json")
        
    def get_info(self):
        """Return plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
        
    def create_default_config(self):
        """Create default plugin configuration"""
        config = {
            "plugin_directories": [
                os.path.join(os.path.expanduser("~"), ".creepyai", "plugins"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins")
            ],
            "disabled_plugins": [],
            "plugin_settings": {}
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Write config
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)
            
        return config
        
    def load_config(self):
        """Load plugin configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading plugin config: {e}")
                
        return self.create_default_config()
        
    def run(self):
        """Initialize the plugin system"""
        config = self.load_config()
        
        # Create plugin directories if they don't exist
        for directory in config.get("plugin_directories", []):
            os.makedirs(directory, exist_ok=True)
            
        return {
            "status": "initialized",
            "config_file": self.config_file,
            "directories": config.get("plugin_directories", [])
        }

# Make sure the plugin directory is in the Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import key plugin modules
from app.plugins.plugins_manager import PluginsManager
from app.plugins.plugin_registry import registry
from app.plugins.plugin_data_manager import data_manager


def setup_logging(config_file: str = None) -> None:
    """
    Set up logging based on the configuration file
    """
    if not config_file:
        # Use default location
        config_file = os.path.join(SCRIPT_DIR, 'logging_config.json')
        
    # Create logs directory if it doesn't exist
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
                
            # Update log file paths if they're relative
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
    """
    Load the plugin configuration from YAML file
    """
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
    """
    Initialize the plugin system
    """
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
        description="Initialize and setup plugin system for CreepyAI"
    )
    parser.add_argument(
        "--config",
        help="Path to the plugin configuration file",
        default=os.path.join(SCRIPT_DIR, 'plugins.yaml')
    )
    parser.add_argument(
        "--log-config",
        help="Path to the logging configuration file",
        default=os.path.join(SCRIPT_DIR, 'logging_config.json')
    )
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_config)
    
    # Load plugin configuration
    config = load_plugin_config(args.config)
    
    # Initialize plugins
    plugin_manager = initialize_plugins(config=config)
    
    # Handle signals for clean shutdown
    handle_signals(plugin_manager)
    
    logger.info("Plugin system initialized successfully")
    
    # Keep the main thread alive
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()