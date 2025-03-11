#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
from yapsy.PluginManager import PluginManagerSingleton
from app.models.PluginManager import PluginManager
from app.models.InputPlugin import InputPlugin

logger = logging.getLogger(__name__)

class UnifiedPluginManager:
    """
    Bridge between the yapsy-based plugin system and the new PluginManager.
    Provides a unified interface to access plugins.
    """
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.yapsy_manager = PluginManagerSingleton.get()
        self.new_manager = PluginManager.get_instance()
        self._initialized = False
        
    def initialize(self, plugin_paths=None):
        """Initialize both plugin managers with the same paths"""
        if self._initialized:
            return
            
        if not plugin_paths:
            plugin_paths = [os.path.join(os.getcwd(), 'plugins')]
            
        # Initialize yapsy manager
        self.yapsy_manager.setCategoriesFilter({'Input': InputPlugin})
        self.yapsy_manager.setPluginPlaces(plugin_paths)
        self.yapsy_manager.locatePlugins()
        self.yapsy_manager.loadPlugins()
        
        # Initialize new manager
        self.new_manager.set_plugin_paths(plugin_paths)
        self.new_manager.discover_plugins()
        
        self._initialized = True
        logger.info(f"Unified plugin manager initialized with {len(self.get_all_plugins())} plugins")
        
    def get_all_plugins(self):
        """Get all available plugins"""
        return self.yapsy_manager.getAllPlugins()
    
    def get_plugin_by_name(self, name, category="Input"):
        """Get a plugin by name and category"""
        return self.yapsy_manager.getPluginByName(name, category)
    
    def get_plugin_instance(self, name):
        """Get plugin instance by name"""
        plugin = self.get_plugin_by_name(name)
        if plugin:
            return plugin.plugin_object
        return self.new_manager.get_plugin(name)
    
    def run_plugin_method(self, plugin_name, method, *args, **kwargs):
        """Run a method on a plugin"""
        plugin_instance = self.get_plugin_instance(plugin_name)
        if not plugin_instance:
            logger.error(f"Plugin {plugin_name} not found")
            return None
            
        if not hasattr(plugin_instance, method):
            logger.error(f"Method {method} not found in plugin {plugin_name}")
            return None
            
        try:
            return getattr(plugin_instance, method)(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error running {method} on {plugin_name}: {str(e)}")
            return None

class Plugin:
    """Plugin integration tool"""
    
    def __init__(self):
        self.name = "Plugin Integration"
        self.description = "Integrates different plugin systems"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        self.legacy_plugins = []
        
    def get_info(self):
        """Return plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
        
    def scan_legacy_plugins(self, directory):
        """Scan for legacy plugins in the given directory"""
        results = []
        
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.error(f"Directory not found: {directory}")
            return results
            
        # This would be implemented to scan for legacy plugin formats
        # For example, yapsy-style plugins with .yapsy-plugin descriptor files
        
        return results
        
    def adapt_legacy_plugin(self, legacy_plugin):
        """Adapt a legacy plugin to the new plugin system"""
        # This would wrap a legacy plugin in an adapter to make it compatible
        # with the new system
        return None
        
    def run(self, legacy_dir=None):
        """Run the integration for the given legacy plugin directory"""
        if not legacy_dir:
            return {"error": "No legacy plugin directory specified"}
            
        legacy_plugins = self.scan_legacy_plugins(legacy_dir)
        adapted_plugins = []
        
        for plugin in legacy_plugins:
            adapted = self.adapt_legacy_plugin(plugin)
            if adapted:
                adapted_plugins.append(adapted)
                
        return {
            "legacy_found": len(legacy_plugins),
            "adapted": len(adapted_plugins),
            "plugins": adapted_plugins
        }
