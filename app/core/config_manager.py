"""
Configuration management for CreepyAI.

This module handles loading, validating, and accessing configuration settings.
"""
import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger('creepyai.core.config')

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path=None):
        self.config = {}
        self.config_path = config_path
        
        # Default locations to search for config files
        self.default_config_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'app', 'app_config.json'),
            os.path.join(os.path.expanduser('~'), '.creepyai', 'config.json'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml'),
        ]
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from file
        
        Returns:
            bool: True if configuration was loaded successfully
        """
        # If a specific config path was provided, try it first
        if self.config_path and os.path.exists(self.config_path):
            if self._load_config_file(self.config_path):
                return True
        
        # Otherwise try default locations
        for path in self.default_config_paths:
            if os.path.exists(path):
                if self._load_config_file(path):
                    self.config_path = path
                    return True
        
        # If no config files found, use fallback defaults
        logger.warning("No configuration files found, using defaults")
        self._load_defaults()
        return False
    
    def _load_config_file(self, path: str) -> bool:
        """
        Load configuration from a specific file
        
        Args:
            path: Path to configuration file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(path, 'r') as f:
                if path.endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
                
                if config:
                    self.config = config
                    logger.info(f"Configuration loaded from {path}")
                    return True
                
                logger.warning(f"Empty configuration file: {path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading configuration from {path}: {e}")
            return False
    
    def _load_defaults(self):
        """Load default configuration settings"""
        # Import defaults module if available
        try:
            from config.defaults import DEFAULT_CONFIG
            self.config = DEFAULT_CONFIG
            logger.info("Loaded configuration from defaults module")
        except ImportError:
            logger.warning("Defaults module not found, using built-in defaults")
            self.config = {
                'app': {
                    'name': 'CreepyAI',
                    'version': '2.5.0',
                    'debug': False,
                    'data_directory': os.path.join(os.path.dirname(__file__), '..', '..', 'data'),
                    'temp_directory': os.path.join(os.path.dirname(__file__), '..', '..', 'temp'),
                    'projects_directory': os.path.join(os.path.dirname(__file__), '..', '..', 'projects'),
                },
                'plugins': {
                    'directory': os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'src'),
                    'configs_directory': os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'configs'),
                },
                'ui': {
                    'theme': 'light',
                    'start_maximized': False,
                    'window_width': 1024,
                    'window_height': 768,
                },
                'geo': {
                    'default_map_center': [51.505, -0.09],  # London
                    'default_zoom': 13,
                }
            }
    
    def save_config(self, path: Optional[str] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            path: Path to save configuration to, defaults to current config_path
            
        Returns:
            bool: True if saved successfully
        """
        save_path = path or self.config_path
        
        if not save_path:
            save_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'app', 'app_config.json')
            logger.warning(f"No config path specified, using default: {save_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            with open(save_path, 'w') as f:
                if save_path.endswith(('.yaml', '.yml')):
                    yaml.dump(self.config, f, default_flow_style=False)
                else:
                    json.dump(self.config, f, indent=2)
                
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to {save_path}: {e}")
            return False
    
    def get(self, key, default=None):
        """
        Get a configuration value by key
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
