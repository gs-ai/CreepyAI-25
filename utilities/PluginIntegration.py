#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
from yapsy.PluginManager import PluginManagerSingleton
from models.PluginManager import PluginManager
from models.InputPlugin import InputPlugin

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
