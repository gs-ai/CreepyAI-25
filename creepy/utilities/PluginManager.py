#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging
from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(os.getcwd(), 'creepy_plugins.log'))
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class PluginManagerUtils:
    """Utility class for managing CreepyAI plugins"""
    
    @staticmethod
    def initialize_plugins():
        """
        Initialize the plugin manager with all available plugins
        Returns the plugin manager instance
        """
        try:
            plugin_manager = PluginManagerSingleton.get()
            plugin_manager.setCategoriesFilter({'Input': InputPlugin})
            
            # Search in multiple possible locations
            plugin_places = [
                os.path.join(os.getcwd(), 'plugins'),
                '/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'
            ]
            
            plugin_manager.setPluginPlaces(plugin_places)
            plugin_manager.collectPlugins()
            
            # Count the plugins found
            plugin_count = len(plugin_manager.getAllPlugins())
            logger.info(f"Found {plugin_count} plugins")
            
            return plugin_manager
        except Exception as e:
            logger.error(f"Error initializing plugins: {str(e)}")
            return None
    
    @staticmethod
    def get_plugin_by_name(name):
        """
        Get a plugin by name
        """
        try:
            plugin_manager = PluginManagerSingleton.get()
            return plugin_manager.getPluginByName(name, 'Input')
        except Exception as e:
            logger.error(f"Error getting plugin {name}: {str(e)}")
            return None
            
    @staticmethod
    def get_configured_plugins():
        """
        Get a list of all plugins that are properly configured
        """
        try:
            plugin_manager = PluginManagerSingleton.get()
            configured_plugins = []
            
            for plugin_info in plugin_manager.getAllPlugins():
                if plugin_info.plugin_object.isConfigured()[0]:
                    configured_plugins.append(plugin_info)
                    
            return configured_plugins
        except Exception as e:
            logger.error(f"Error getting configured plugins: {str(e)}")
            return []
    
    @staticmethod
    def reload_all_plugins():
        """
        Reload all plugins from disk
        """
        try:
            plugin_manager = PluginManagerSingleton.get()
            plugin_manager.collectPlugins()
            return True
        except Exception as e:
            logger.error(f"Error reloading plugins: {str(e)}")
            return False
