"""
Settings manager for CreepyAI.
Handles loading, saving, and validating application settings.
"""

import os
import json
import yaml
import logging
import configparser
from pathlib import Path

logger = logging.getLogger(__name__)

class SettingsManager:
    """
    Manager for application settings.
    Handles loading, saving, and accessing configuration files.
    """
    
    def __init__(self):
        """Initialize the settings manager."""
        self.config_root = os.path.dirname(os.path.abspath(__file__))
        self.app_config_dir = os.path.join(self.config_root, 'app')
        self.logging_config_dir = os.path.join(self.config_root, 'logging')
        self.plugins_config_dir = os.path.join(self.config_root, 'plugins')
        self._app_config = None
        self._plugins_config = {}
        self._default_values = {}
        
        # Make sure we have our directories
        for dir_path in [self.app_config_dir, self.logging_config_dir, self.plugins_config_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Load default values
        self._load_defaults()

    def _load_defaults(self):
        """Load default values from defaults.py"""
        try:
            from . import defaults
            self._default_values = defaults.DEFAULT_SETTINGS
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load default settings: {e}")
            self._default_values = {}

    def get_app_config(self, reload=False):
        """
        Get application configuration.
        
        Args:
            reload: Force reload from disk if True
            
        Returns:
            Dictionary containing application configuration
        """
        if self._app_config is None or reload:
            app_config_path = os.path.join(self.app_config_dir, 'app_config.json')
            try:
                if os.path.exists(app_config_path):
                    with open(app_config_path, 'r') as f:
                        self._app_config = json.load(f)
                else:
                    # Use defaults if file doesn't exist
                    self._app_config = self._default_values.get('app', {})
                    # Save the defaults to disk
                    self.save_app_config()
            except Exception as e:
                logger.error(f"Error loading app config: {e}")
                self._app_config = self._default_values.get('app', {})
        
        return self._app_config
    
    def save_app_config(self):
        """Save application configuration to disk."""
        if self._app_config is None:
            return
        
        app_config_path = os.path.join(self.app_config_dir, 'app_config.json')
        try:
            with open(app_config_path, 'w') as f:
                json.dump(self._app_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving app config: {e}")
    
    def get_plugin_config(self, plugin_name, reload=False):
        """
        Get configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            reload: Force reload from disk if True
            
        Returns:
            Dictionary containing plugin configuration
        """
        if plugin_name not in self._plugins_config or reload:
            plugin_config_path = os.path.join(self.plugins_config_dir, f"{plugin_name}.conf")
            
            try:
                if os.path.exists(plugin_config_path):
                    config = configparser.ConfigParser()
                    config.read(plugin_config_path)
                    
                    # Convert to dictionary
                    plugin_config = {}
                    for section in config.sections():
                        plugin_config[section] = dict(config[section])
                    
                    self._plugins_config[plugin_name] = plugin_config
                else:
                    # Use defaults if file doesn't exist
                    plugin_defaults = self._default_values.get('plugins', {}).get(plugin_name, {})
                    self._plugins_config[plugin_name] = plugin_defaults
                    # Save the defaults to disk
                    self.save_plugin_config(plugin_name)
            except Exception as e:
                logger.error(f"Error loading plugin config for {plugin_name}: {e}")
                self._plugins_config[plugin_name] = {}
        
        return self._plugins_config[plugin_name]
    
    def save_plugin_config(self, plugin_name):
        """
        Save plugin configuration to disk.
        
        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name not in self._plugins_config:
            return
        
        plugin_config_path = os.path.join(self.plugins_config_dir, f"{plugin_name}.conf")
        try:
            config = configparser.ConfigParser()
            
            # Convert dictionary to ConfigParser
            plugin_config = self._plugins_config[plugin_name]
            for section, options in plugin_config.items():
                config[section] = options
            
            with open(plugin_config_path, 'w') as f:
                config.write(f)
        except Exception as e:
            logger.error(f"Error saving plugin config for {plugin_name}: {e}")
    
    def get_plugins_list(self):
        """
        Get list of available plugins from plugins.yaml.
        
        Returns:
            List of plugin information dictionaries
        """
        plugins_yaml_path = os.path.join(self.plugins_config_dir, 'plugins.yaml')
        try:
            if os.path.exists(plugins_yaml_path):
                with open(plugins_yaml_path, 'r') as f:
                    plugins_data = yaml.safe_load(f)
                return plugins_data.get('plugins', [])
            else:
                return []
        except Exception as e:
            logger.error(f"Error loading plugins list: {e}")
            return []
    
    def get_logging_config(self):
        """
        Get logging configuration.
        
        Returns:
            Dictionary containing logging configuration
        """
        logging_config_path = os.path.join(self.logging_config_dir, 'logging_config.json')
        try:
            if os.path.exists(logging_config_path):
                with open(logging_config_path, 'r') as f:
                    return json.load(f)
            else:
                # Return default logging config
                return self._default_values.get('logging', {})
        except Exception as e:
            logger.error(f"Error loading logging config: {e}")
            return {}

    def update_app_setting(self, key, value):
        """
        Update a specific application setting.
        
        Args:
            key: Setting key
            value: Setting value
        """
        if self._app_config is None:
            self.get_app_config()
        
        self._app_config[key] = value
        self.save_app_config()
    
    def get_app_setting(self, key, default=None):
        """
        Get a specific application setting.
        
        Args:
            key: Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        if self._app_config is None:
            self.get_app_config()
        
        return self._app_config.get(key, default)
