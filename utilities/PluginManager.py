#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import configparser
from yapsy.PluginManager import PluginManager as YapsyPluginManager
from yapsy.PluginInfo import PluginInfo
from yapsy.IPlugin import IPlugin

logger = logging.getLogger('CreepyAI.PluginManager')

class CreepyPluginManager:
    """Class for managing CreepyAI plugins"""
    
    def __init__(self, plugin_dirs=None):
        """Initialize the plugin manager"""
        if plugin_dirs is None:
            # Default plugin directories
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            plugin_dirs = [os.path.join(base_dir, 'plugins')]
        
        self.plugin_dirs = plugin_dirs
        self.manager = YapsyPluginManager()
        self.manager.setPluginPlaces(self.plugin_dirs)
        self.plugin_configs = {}
        
        # Set categories for different plugin types
        self.categories = {
            'input': 'Input',
            'analysis': 'Analysis',
            'export': 'Export'
        }
        
        # Load plugins
        self.load_plugins()
    
    def load_plugins(self):
        """Load all plugins from plugin directories"""
        logger.info("Loading plugins...")
        
        # Collect plugins
        self.manager.collectPlugins()
        
        # Load plugin configurations
        self._load_plugin_configs()
        
        logger.info(f"Loaded {len(self.get_all_plugins())} plugins")
    
    def _load_plugin_configs(self):
        """Load configuration for all plugins"""
        for plugin_info in self.get_all_plugins():
            self._load_plugin_config(plugin_info)
    
    def _load_plugin_config(self, plugin_info):
        """Load configuration for a single plugin"""
        config_file = plugin_info.path + '.conf'
        
        if not os.path.exists(config_file):
            logger.warning(f"Config file not found for plugin: {plugin_info.name}")
            self.plugin_configs[plugin_info.name] = {}
            return
        
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            self.plugin_configs[plugin_info.name] = dict(config['Configuration'])
            logger.debug(f"Loaded config for plugin: {plugin_info.name}")
        except Exception as e:
            logger.error(f"Failed to load config for plugin {plugin_info.name}: {e}")
            self.plugin_configs[plugin_info.name] = {}
    
    def get_all_plugins(self):
        """Get a list of all available plugins"""
        return self.manager.getAllPlugins()
    
    def get_plugins_by_category(self, category):
        """Get plugins by category"""
        return [p for p in self.get_all_plugins() if p.category == category]
    
    def get_input_plugins(self):
        """Get all input plugins"""
        return self.get_plugins_by_category(self.categories['input'])
    
    def get_analysis_plugins(self):
        """Get all analysis plugins"""
        return self.get_plugins_by_category(self.categories['analysis'])
    
    def get_export_plugins(self):
        """Get all export plugins"""
        return self.get_plugins_by_category(self.categories['export'])
    
    def activate_plugin(self, plugin_info):
        """Activate a plugin"""
        self.manager.activatePluginByName(plugin_info.name, plugin_info.category)
        logger.info(f"Activated plugin: {plugin_info.name}")
    
    def deactivate_plugin(self, plugin_info):
        """Deactivate a plugin"""
        self.manager.deactivatePluginByName(plugin_info.name, plugin_info.category)
        logger.info(f"Deactivated plugin: {plugin_info.name}")
    
    def get_plugin_config(self, plugin_name):
        """Get configuration for a plugin"""
        return self.plugin_configs.get(plugin_name, {})
    
    def save_plugin_config(self, plugin_name, config):
        """Save configuration for a plugin"""
        self.plugin_configs[plugin_name] = config
        
        # Get the plugin info to get the path
        plugin_info = self._get_plugin_info_by_name(plugin_name)
        if not plugin_info:
            logger.error(f"Cannot save config for unknown plugin: {plugin_name}")
            return False
        
        config_file = plugin_info.path + '.conf'
        
        try:
            parser = configparser.ConfigParser()
            parser['Configuration'] = config
            
            with open(config_file, 'w') as f:
                parser.write(f)
            
            logger.info(f"Saved config for plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config for plugin {plugin_name}: {e}")
            return False
    
    def _get_plugin_info_by_name(self, plugin_name):
        """Get plugin info by name"""
        for plugin_info in self.get_all_plugins():
            if plugin_info.name == plugin_name:
                return plugin_info
        return None

"""
PluginManager Compatibility Layer

This module provides backward compatibility with the original PluginManager
while using the new unified PluginManager from the models directory.
"""
import os
import sys
import logging
import importlib
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Try to import the new PluginManager
try:
    from models.PluginManager import PluginManager as NewPluginManager
    USE_NEW_MANAGER = True
except ImportError:
    USE_NEW_MANAGER = False
    logger.warning("Could not import the new PluginManager, using legacy implementation")

class PluginManager:
    """
    Compatibility layer for the PluginManager
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = PluginManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the plugin manager"""
        if PluginManager._instance is not None:
            return
            
        self.plugins = {}
        self.plugin_paths = []
        
        # Use the new manager if available
        if USE_NEW_MANAGER:
            self.new_manager = NewPluginManager.get_instance()
        else:
            self.new_manager = None
        
    def set_plugin_paths(self, paths):
        """Set plugin paths"""
        self.plugin_paths = paths
        if self.new_manager:
            self.new_manager.set_plugin_paths(paths)
    
    def discover_plugins(self):
        """Discover available plugins"""
        if self.new_manager:
            return self.new_manager.discover_plugins()
        else:
            # Legacy implementation
            self.plugins = {}
            # Implementation similar to old PluginManager
            return self.plugins
    
    def get_plugin(self, name):
        """Get a plugin by name"""
        if self.new_manager:
            return self.new_manager.get_plugin(name)
        else:
            # Legacy implementation
            return self.plugins.get(name, {}).get('instance')
    
    def get_plugin_names(self):
        """Get all plugin names"""
        if self.new_manager:
            return self.new_manager.get_plugin_names()
        else:
            # Legacy implementation
            return list(self.plugins.keys())
    
    def run_plugin(self, name, method, *args, **kwargs):
        """Run a plugin method"""
        if self.new_manager:
            return self.new_manager.run_plugin(name, method, *args, **kwargs)
        else:
            # Legacy implementation
            plugin = self.get_plugin(name)
            if not plugin:
                return None
            if not hasattr(plugin, method):
                return None
            try:
                return getattr(plugin, method)(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error running plugin {name}.{method}: {e}")
                return None
