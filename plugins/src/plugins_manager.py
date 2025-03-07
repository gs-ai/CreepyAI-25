#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Manager for CreepyAI
Handles plugin discovery, loading, and management
"""

import os
import sys
import importlib
import logging
import inspect
import yaml
import json
from typing import Dict, List, Any, Optional, Type, Set
import traceback

from plugins.base_plugin import BasePlugin
from config import get_plugins_config, get_logging_config

logger = logging.getLogger(__name__)

class PluginsManager:
    """
    Manager for CreepyAI plugins that handles discovery, loading, and management
    """
    
    def __init__(self, plugins_dir: str = None):
        """
        Initialize the plugin manager
        
        Args:
            plugins_dir: Directory containing plugins
        """
        # Set plugins directory
        if plugins_dir:
            self.plugins_dir = plugins_dir
        else:
            self.plugins_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Dictionary of loaded plugin instances
        self.plugin_instances = {}
        
        # Dictionary of discovered plugins
        self.discovered_plugins = {}
        
        # Plugin configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration for plugins"""
        config = {}
        
        # Try to load from plugins.yaml
        config_file = os.path.join(self.plugins_dir, 'plugins.yaml')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading plugin config: {e}")
                
        return config
    
    def discover_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover available plugins in the plugins directory
        
        Returns:
            Dictionary mapping plugin IDs to information dictionaries
        """
        plugins = {}
        
        # Ensure plugins directory exists
        if not os.path.exists(self.plugins_dir):
            logger.error(f"Plugins directory does not exist: {self.plugins_dir}")
            return plugins
            
        # Look for Python files that might be plugins
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]  # Remove .py extension
                
                # Skip common utility modules
                if module_name in ['base_plugin', 'plugins_manager', 'plugin_registry', 
                                  'plugin_data_manager', 'plugin_monitor']:
                    continue
                
                # Try to import the module to see if it contains a plugin class
                try:
                    # Import the module (as full path to avoid conflicts)
                    module_spec = importlib.util.find_spec(f"plugins.{module_name}")
                    if module_spec is None:
                        continue
                        
                    module = importlib.import_module(f"plugins.{module_name}")
                    
                    # Find the plugin class (subclass of BasePlugin)
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and issubclass(obj, BasePlugin) and 
                            obj != BasePlugin and name != 'BasePlugin'):
                            
                            # Create a temporary instance to get metadata
                            try:
                                instance = obj()
                                plugins[module_name] = {
                                    'name': instance.name,
                                    'description': instance.description,
                                    'version': instance.version,
                                    'author': instance.author,
                                    'class': name,
                                    'module': module_name,
                                    'path': os.path.join(self.plugins_dir, filename)
                                }
                                
                                # Don't keep the instance, we'll create a new one when loading
                                del instance
                                
                                # We found a plugin class, no need to continue this loop
                                break
                                
                            except Exception as e:
                                logger.warning(f"Error creating temporary instance of {name}: {e}")
                                continue
                
                except Exception as e:
                    logger.warning(f"Error discovering plugin in {filename}: {e}")
                    continue
        
        self.discovered_plugins = plugins
        return plugins
    
    def load_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """
        Load a specific plugin by ID
        
        Args:
            plugin_id: Identifier of the plugin to load
            
        Returns:
            Plugin instance or None if loading failed
        """
        # Return existing instance if already loaded
        if plugin_id in self.plugin_instances:
            return self.plugin_instances[plugin_id]
            
        # Discover plugins if not already done
        if not self.discovered_plugins:
            self.discover_plugins()
            
        # Check if plugin_id exists
        if plugin_id not in self.discovered_plugins:
            logger.warning(f"Unknown plugin ID: {plugin_id}")
            return None
            
        plugin_info = self.discovered_plugins[plugin_id]
        
        try:
            # Import the module
            module = importlib.import_module(f"plugins.{plugin_info['module']}")
            
            # Get the plugin class
            plugin_class = getattr(module, plugin_info['class'])
            
            # Create an instance
            instance = plugin_class()
            
            # Apply configuration if available
            plugin_config = self.config.get('plugins', {}).get(plugin_id, {}).get('config', {})
            if plugin_config:
                instance.configure(plugin_config)
            
            # Store the instance
            self.plugin_instances[plugin_id] = instance
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Discover and load all available plugins
        
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        # Discover plugins
        plugins = self.discover_plugins()
        
        # Load each plugin
        for plugin_id in plugins:
            # Skip plugins that are disabled in config
            if self.config.get('plugins', {}).get(plugin_id, {}).get('enabled', True) is False:
                logger.info(f"Skipping disabled plugin: {plugin_id}")
                continue
                
            self.load_plugin(plugin_id)
            
        return self.plugin_instances
    
    def get_plugins_by_capability(self, capability: str) -> Dict[str, BasePlugin]:
        """
        Get all plugins that provide a specific capability
        
        Args:
            capability: Name of the capability to look for
            
        Returns:
            Dictionary mapping plugin IDs to plugin instances
        """
        result = {}
        
        try:
            # Import registry to check capabilities
            from plugins.plugin_registry import registry
            
            if registry.has_capability(capability):
                provider = registry.get_capability_provider(capability)
                if provider:
                    plugin = self.load_plugin(provider)
                    if plugin:
                        result[provider] = plugin
        except ImportError:
            logger.warning("Could not import plugin registry")
            
        return result
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin
        
        Args:
            plugin_id: ID of the plugin to unload
            
        Returns:
            True if plugin was unloaded, False otherwise
        """
        if plugin_id in self.plugin_instances:
            try:
                # Call cleanup method if it exists
                self.plugin_instances[plugin_id].cleanup()
                
                # Remove from loaded plugins
                del self.plugin_instances[plugin_id]
                
                return True
                
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_id}: {e}")
                
        return False
    
    def reload_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """
        Reload a plugin
        
        Args:
            plugin_id: ID of the plugin to reload
            
        Returns:
            Reloaded plugin instance or None if reloading failed
        """
        # Unload the plugin
        self.unload_plugin(plugin_id)
        
        # Reload the module
        if plugin_id in self.discovered_plugins:
            module_name = f"plugins.{self.discovered_plugins[plugin_id]['module']}"
            try:
                # Force module reload
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
            except Exception as e:
                logger.error(f"Error reloading module for plugin {plugin_id}: {e}")
        
        # Load the plugin again
        return self.load_plugin(plugin_id)
