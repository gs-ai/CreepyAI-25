"""
Configuration Manager for CreepyAI
Handles reading, writing, and managing application configuration
"""

import os
import sys
import logging
import json
import yaml
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from PyQt5.QtCore import QSettings

from app.core.include.constants import SettingsKey
from app.core.path_utils import (
    get_user_config_dir, get_user_data_dir, get_app_root
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages application configuration settings
    
    Provides a unified interface for accessing configuration settings from
    various sources (QSettings, config files, etc.)
    """

    def __init__(self):
        """Initialize the configuration manager"""
        self.qsettings = QSettings("CreepyAI", "Application")
        self.config_dir = get_user_config_dir()
        self.app_root = get_app_root()
        self.data_dir = self._get_data_dir()
        
        # Cache for config files
        self._config_cache = {}
        
    def _get_data_dir(self) -> Path:
        """Get the configured data directory"""
        configured_dir = self.qsettings.value(SettingsKey.DATA_DIRECTORY, "")
        
        if configured_dir and os.path.exists(configured_dir):
            return Path(configured_dir)
        else:
            # Use default data directory
            data_dir = get_user_data_dir()
            self.qsettings.setValue(SettingsKey.DATA_DIRECTORY, str(data_dir))
            return data_dir

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value from QSettings
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default if not found
        """
        return self.qsettings.value(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value in QSettings
        
        Args:
            key: Setting key
            value: Value to set
        """
        self.qsettings.setValue(key, value)
    
    def load_json_config(self, config_path: str, cache: bool = True) -> Dict:
        """
        Load a JSON configuration file
        
        Args:
            config_path: Path to the configuration file (relative to config_dir or absolute)
            cache: Whether to cache the configuration
            
        Returns:
            Dictionary with configuration values
        """
        # Check cache first
        if cache and config_path in self._config_cache:
            return self._config_cache[config_path]
            
        # Determine full path
        full_path = self._resolve_config_path(config_path)
        
        if not os.path.exists(full_path):
            logger.warning(f"Configuration file not found: {full_path}")
            return {}
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Cache if requested
            if cache:
                self._config_cache[config_path] = config
                
            return config
        except Exception as e:
            logger.error(f"Error loading configuration from {full_path}: {e}")
            return {}
    
    def load_yaml_config(self, config_path: str, cache: bool = True) -> Dict:
        """
        Load a YAML configuration file
        
        Args:
            config_path: Path to the configuration file (relative to config_dir or absolute)
            cache: Whether to cache the configuration
            
        Returns:
            Dictionary with configuration values
        """
        # Check cache first
        if cache and config_path in self._config_cache:
            return self._config_cache[config_path]
            
        # Determine full path
        full_path = self._resolve_config_path(config_path)
        
        if not os.path.exists(full_path):
            logger.warning(f"Configuration file not found: {full_path}")
            return {}
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Cache if requested
            if cache:
                self._config_cache[config_path] = config
                
            return config
        except Exception as e:
            logger.error(f"Error loading configuration from {full_path}: {e}")
            return {}
    
    def save_json_config(self, config_path: str, config: Dict) -> bool:
        """
        Save a configuration dictionary to a JSON file
        
        Args:
            config_path: Path to the configuration file (relative to config_dir or absolute)
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        # Determine full path
        full_path = self._resolve_config_path(config_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Update cache
            self._config_cache[config_path] = config
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {full_path}: {e}")
            return False
    
    def save_yaml_config(self, config_path: str, config: Dict) -> bool:
        """
        Save a configuration dictionary to a YAML file
        
        Args:
            config_path: Path to the configuration file (relative to config_dir or absolute)
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        # Determine full path
        full_path = self._resolve_config_path(config_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, default_flow_style=False)
            
            # Update cache
            self._config_cache[config_path] = config
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {full_path}: {e}")
            return False
    
    def get_plugin_config(self, plugin_name: str) -> Dict:
        """
        Get configuration for a specific plugin
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dictionary with plugin configuration
        """
        # Try to find a plugin-specific config file
        plugin_config_file = f"{plugin_name}.json"
        plugin_config_path = os.path.join("plugins", plugin_config_file)
        
        # First try user config dir
        config = self.load_json_config(plugin_config_path, cache=False)
        
        if not config:
            # Try app default configs
            app_config_path = os.path.join(self.app_root, "configs", "plugins", plugin_config_file)
            if os.path.exists(app_config_path):
                try:
                    with open(app_config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading plugin configuration from {app_config_path}: {e}")
        
        return config
    
    def save_plugin_config(self, plugin_name: str, config: Dict) -> bool:
        """
        Save configuration for a specific plugin
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        plugin_config_path = os.path.join("plugins", f"{plugin_name}.json")
        return self.save_json_config(plugin_config_path, config)
    
    def _resolve_config_path(self, config_path: str) -> str:
        """
        Resolve a configuration path
        
        If path is absolute, use it as-is.
        If path is relative, resolve relative to config_dir.
        
        Args:
            config_path: Path to resolve
            
        Returns:
            Absolute path
        """
        if os.path.isabs(config_path):
            return config_path
        else:
            return os.path.join(self.config_dir, config_path)
    
    def clear_cache(self) -> None:
        """Clear the configuration cache"""
        self._config_cache.clear()
    
    def get_recent_projects(self) -> List[str]:
        """
        Get list of recently opened projects
        
        Returns:
            List of project paths
        """
        return self.qsettings.value(SettingsKey.RECENT_PROJECTS, [], type=list)
    
    def add_recent_project(self, project_path: str, max_recent: int = 10) -> None:
        """
        Add a project to the recent projects list
        
        Args:
            project_path: Path to the project file
            max_recent: Maximum number of recent projects to keep
        """
        recent_projects = self.get_recent_projects()
        
        # Remove project if it's already in the list
        if project_path in recent_projects:
            recent_projects.remove(project_path)
            
        # Add project to the beginning of the list
        recent_projects.insert(0, project_path)
        
        # Trim list if necessary
        recent_projects = recent_projects[:max_recent]
        
        # Save updated list
        self.qsettings.setValue(SettingsKey.RECENT_PROJECTS, recent_projects)
