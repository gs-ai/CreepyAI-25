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

class PluginManager:
    """
    Manages CreepyAI plugins that use web scraping instead of APIs.
    """
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.plugin_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'plugins'
        )
        
        # Create plugin manager
        self.manager = YapsyPluginManager()
        self.manager.setPluginPlaces([self.plugin_path])
        self.manager.setCategoriesFilter({
            "Input": IPlugin,
        })
        
        # Plugin collections
        self.plugins = []
        self.active_plugins = []
        self.plugin_info = {}
        
        logger.info(f"Plugin manager initialized with plugin path: {self.plugin_path}")
    
    def load_plugins(self):
        """Load all available plugins."""
        try:
            self.manager.collectPlugins()
            
            # Get all plugins
            plugin_count = 0
            failed_count = 0
            
            for plugin_info in self.manager.getAllPlugins():
                try:
                    plugin_name = plugin_info.name
                    plugin_obj = plugin_info.plugin_object
                    
                    logger.info(f"Found plugin: {plugin_name}")
                    
                    # Store plugin info
                    self.plugins.append(plugin_obj)
                    self.plugin_info[plugin_name] = {
                        'name': plugin_name,
                        'description': plugin_info.description,
                        'author': getattr(plugin_info, 'author', 'Unknown'),
                        'version': getattr(plugin_info, 'version', '1.0'),
                        'website': getattr(plugin_info, 'website', ''),
                        'object': plugin_obj,
                    }
                    
                    # Try to activate the plugin
                    self.manager.activatePluginByName(plugin_name)
                    plugin_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_info.name}: {str(e)}")
                    failed_count += 1
                    
            logger.info(f"Loaded {plugin_count} plugins. Failed to load {failed_count} plugins.")
            
        except Exception as e:
            logger.error(f"Error loading plugins: {str(e)}")
    
    def get_plugin(self, plugin_name):
        """Get a plugin by name."""
        if plugin_name in self.plugin_info:
            return self.plugin_info[plugin_name]['object']
        return None
    
    def get_active_plugins(self):
        """Get all active plugins."""
        active_plugins = []
        for plugin in self.plugins:
            if plugin.is_activated:
                active_plugins.append(plugin)
        return active_plugins
    
    def configure_plugins(self, config_manager, database):
        """Configure all plugins with settings and database."""
        for plugin in self.plugins:
            try:
                # Check if the plugin has these methods before calling
                if hasattr(plugin, 'set_config_manager'):
                    plugin.set_config_manager(config_manager)
                
                if hasattr(plugin, 'set_database'):
                    plugin.set_database(database)
                    
                logger.debug(f"Configured plugin: {plugin.name}")
                
            except Exception as e:
                logger.error(f"Error configuring plugin {plugin.name}: {str(e)}")
    
    def load_dynamic_plugins(self, plugin_dirs=None):
        """Load plugins from additional directories."""
        if not plugin_dirs:
            return
            
        for plugin_dir in plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
                
            self.manager.setPluginPlaces([plugin_dir])
            self.manager.collectPlugins()
            
            # Process newly discovered plugins
            for plugin_info in self.manager.getAllPlugins():
                if plugin_info.name not in self.plugin_info:
                    try:
                        plugin_name = plugin_info.name
                        plugin_obj = plugin_info.plugin_object
                        
                        logger.info(f"Found dynamic plugin: {plugin_name} in {plugin_dir}")
                        
                        # Store plugin info
                        self.plugins.append(plugin_obj)
                        self.plugin_info[plugin_name] = {
                            'name': plugin_name,
                            'description': plugin_info.description,
                            'author': getattr(plugin_info, 'author', 'Unknown'),
                            'version': getattr(plugin_info, 'version', '1.0'),
                            'website': getattr(plugin_info, 'website', ''),
                            'object': plugin_obj,
                            'dynamic': True,
                            'path': plugin_dir
                        }
                        
                        # Try to activate the plugin
                        self.manager.activatePluginByName(plugin_name)
                        
                    except Exception as e:
                        logger.error(f"Failed to load dynamic plugin {plugin_info.name}: {str(e)}")
    
    def get_plugin_settings_schema(self, plugin_name):
        """Get the settings schema for a plugin."""
        plugin = self.get_plugin(plugin_name)
        if plugin and hasattr(plugin, 'get_settings_schema'):
            return plugin.get_settings_schema()
        return {}
    
    def run_plugin(self, plugin_name, target, search_params=None):
        """
        Run a specific plugin to search for locations.
        
        Args:
            plugin_name: Name of the plugin to run
            target: Target information (name, username, etc.)
            search_params: Additional search parameters
            
        Returns:
            list: List of locations found
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin {plugin_name} not found")
            return []
            
        if not hasattr(plugin, 'search_locations'):
            logger.error(f"Plugin {plugin_name} does not implement search_locations method")
            return []
            
        try:
            logger.info(f"Running plugin: {plugin_name}")
            locations = plugin.search_locations(target, search_params)
            logger.info(f"Plugin {plugin_name} found {len(locations)} locations")
            return locations
        except Exception as e:
            logger.error(f"Error running plugin {plugin_name}: {str(e)}")
            return []
