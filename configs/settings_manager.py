# This module provides the SettingsManager class for loading"""
Settings manager for CreepyAI.

This module provides the SettingsManager class for loading, saving, and
accessing application settings from various sources.
"""
import os
import sys
import json
import yaml
import logging
import copy
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache

# Add core to path so we can import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'core')))
try:
    from utils import normalize_path, get_app_root
except ImportError:
    # Fallback if import fails
    def normalize_path(path):
        if not path:
            return path
        return os.path.normpath(os.path.expanduser(path))
        
    def get_app_root():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger('creepyai.config.settings')

class SettingsManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SettingsManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, config_dir=None):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('SettingsManager')
        self.app_root = get_app_root()
        
        # Use normalized paths for cross-platform compatibility
        if config_dir:
            self.config_dir = normalize_path(config_dir)
        else:
            self.config_dir = self.app_root
            
        self._config: Dict[str, Any] = {}
        self._default_config: Dict[str, Any] = {}
        
        # List of potential config file locations in order of preference
        config_files = [
            os.path.join(self.app_root, 'configs', 'app_config.json'),
            os.path.join(self.app_root, 'config', 'app_config.json'),
            os.path.join(self.app_root, 'configs', 'settings.json'),
            os.path.join(self.app_root, 'config', 'settings.yaml')
        ]
        
        # Find first existing config file
        self._settings_file = None
        for file_path in config_files:
            if os.path.exists(file_path):
                self._settings_file = file_path
                break
                
        # If no config file found, use default location
        if not self._settings_file:
            self._settings_file = os.path.join(self.app_root, 'configs', 'app_config.json')
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
            
        self._last_reload = 0
        self._watch_thread = None
        self._stop_watching = threading.Event()
        self._observers = []
        self._modified = False
        self._env_prefix = 'CREEPYAI_'
        self._config_path = self._settings_file
        
        # Initialize settings with empty dict
        self._settings = {}
        
        self._load_default_config()
        self._load_config()
        self._initialized = True
        
    def _load_default_config(self):
        """Load default configuration"""
        # Look for defaults in multiple locations
        default_paths = [
            os.path.join(self.config_dir, 'config', 'defaults.py'),
            os.path.join(self.app_root, 'config', 'defaults.py'),
            os.path.join(self.app_root, 'configs', 'defaults.py')
        ]
        
        for default_config_path in default_paths:
            if os.path.exists(default_config_path):
                try:
                    # Try to import defaults module
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("defaults", default_config_path)
                    defaults = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(defaults)
                    
                    self._default_config = getattr(defaults, 'DEFAULT_CONFIG', {})
                    self._settings = copy.deepcopy(self._default_config)
                    self.logger.debug(f"Loaded default configuration from {default_config_path}")
                    break
                except Exception as e:
                    self.logger.error(f"Error loading default config from {default_config_path}: {e}")
        
        # If no defaults found, check for JSON/YAML defaults
        if not self._default_config:
            default_json = os.path.join(self.app_root, 'configs', 'defaults.json')
            default_yaml = os.path.join(self.app_root, 'configs', 'defaults.yaml')
            
            if os.path.exists(default_json):
                try:
                    with open(default_json, 'r', encoding='utf-8') as f:
                        self._default_config = json.load(f)
                        self._settings = copy.deepcopy(self._default_config)
                        self.logger.debug(f"Loaded default configuration from {default_json}")
                except Exception as e:
                    self.logger.error(f"Error loading default config from {default_json}: {e}")
                    
            elif os.path.exists(default_yaml):
                try:
                    with open(default_yaml, 'r', encoding='utf-8') as f:
                        self._default_config = yaml.safe_load(f) or {}
                        self._settings = copy.deepcopy(self._default_config)
                        self.logger.debug(f"Loaded default configuration from {default_yaml}")
                except Exception as e:
                    self.logger.error(f"Error loading default config from {default_yaml}: {e}")
                    
        if not self._default_config:
            self._default_config = {}
            self._settings = {}
        
    def _load_config(self):
        """Load configuration from file with error handling"""
        try:
            if os.path.exists(self._settings_file):
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    if self._settings_file.endswith('.json'):
                        loaded_config = json.load(f)
                    elif self._settings_file.endswith(('.yaml', '.yml')):
                        loaded_config = yaml.safe_load(f)
                    else:
                        self.logger.error(f"Unsupported config file format: {self._settings_file}")
                        loaded_config = {}
                        
                # Merge with defaults
                self._config = self._default_config.copy()
                self._config.update(loaded_config)
                self._last_reload = time.time()
                self.logger.info(f"Loaded configuration from {self._settings_file}")
            else:
                self.logger.warning(f"Config file not found: {self._settings_file}, using defaults")
                self._config = self._default_config.copy()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self._config = self._default_config.copy()
        
    def start_watching(self):
        """Start watching config file for changes"""
        if self._watch_thread and self._watch_thread.is_alive():
            return
            
        self._stop_watching.clear()
        self._watch_thread = threading.Thread(target=self._watch_config_file, daemon=True)
        self._watch_thread.start()
        
    def stop_watching(self):
        """Stop watching config file"""
        if self._watch_thread and self._watch_thread.is_alive():
            self._stop_watching.set()
            self._watch_thread.join(timeout=1.0)
        
    def _watch_config_file(self):
        """Watch config file for changes and reload when needed"""
        check_interval = 5.0  # seconds
        
        while not self._stop_watching.is_set():
            try:
                if os.path.exists(self._settings_file):
                    mtime = os.path.getmtime(self._settings_file)
                    if mtime > self._last_reload:
                        self.logger.info("Config file changed, reloading...")
                        self._load_config()
            except Exception as e:
                self.logger.error(f"Error checking config file: {e}")
                
            self._stop_watching.wait(check_interval)
    
    @lru_cache(maxsize=128)
    def get(self, key, default=None):
        """Get setting value with caching"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key, value):
        """Set setting value and save to file"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the right location
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        self.get.cache_clear()  # Clear the cache
        self._save_config()
        
    def _save_config(self):
        """Save current config to file"""
        try:
            os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
            
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                if self._settings_file.endswith('.json'):
                    json.dump(self._config, f, indent=2)
                elif self._settings_file.endswith(('.yaml', '.yml')):
                    yaml.safe_dump(self._config, f)
                    
            self._last_reload = time.time()
            self.logger.info(f"Configuration saved to {self._settings_file}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def load_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Load default settings
        
        Args:
            defaults: Dictionary of default settings
        """
        self._settings = copy.deepcopy(defaults)
        logger.debug("Default settings loaded")
    
    def load_from_file(self, path: Union[str, Path]) -> bool:
        """
        Load settings from a configuration file
        
        Args:
            path: Path to the configuration file (JSON or YAML)
            
        Returns:
            bool: True if the file was loaded successfully
        """
        if not os.path.exists(path):
            logger.warning(f"Configuration file not found: {path}")
            return False
        
        try:
            with open(path, 'r') as f:
                if str(path).endswith(('.yaml', '.yml')):
                    new_settings = yaml.safe_load(f)
                else:
                    new_settings = json.load(f)
                
            if not new_settings:
                logger.warning(f"Empty configuration file: {path}")
                return False
                
            # Update settings with new values
            self._update_nested_dict(self._settings, new_settings)
            self._config_path = path
            logger.info(f"Settings loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration from {path}: {e}")
            return False
    
    def load_from_env(self) -> None:
        """
        Load settings from environment variables
        
        Environment variables should be prefixed with CREEPYAI_
        and use double underscores for nesting. For example:
        CREEPYAI_APP__DEBUG=true maps to {'app': {'debug': true}}
        """
        for key, value in os.environ.items():
            if key.startswith(self._env_prefix):
                # Remove prefix and split by double underscore
                key_parts = key[len(self._env_prefix):].lower().split('__')
                
                # Convert value to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                # Navigate to the nested dict and set value
                current = self._settings
                for part in key_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value
                current[key_parts[-1]] = value
                logger.debug(f"Setting from environment: {key}")
    
    def load_from_args(self, args_list: List[str]) -> None:
        """
        Load settings from command line arguments
        
        Args:
            args_list: List of command line arguments
        
        Arguments should be in the format --section.key=value
        For example: --app.debug=true
        """
        import re
        
        arg_pattern = re.compile(r'--([a-zA-Z0-9.-]+)=(.+)')
        
        for arg in args_list:
            match = arg_pattern.match(arg)
            if match:
                key_path = match.group(1)
                value = match.group(2)
                
                # Convert value to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                # Set the value using the key path
                self.set(key_path, value)
                logger.debug(f"Setting from command line: {key_path}={value}")
    
    def save(self, path: Optional[Union[str, Path]] = None) -> bool:
        """
        Save current settings to a file
        
        Args:
            path: Path to save the settings to (uses self._config_path if None)
            
        Returns:
            bool: True if the settings were saved successfully
        """
        save_path = path or self._config_path
        
        if not save_path:
            self.logger.error("No save path specified and no config_path set")
            return False
        
        # Normalize the path
        save_path = normalize_path(save_path)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Write settings to file based on file extension
            with open(save_path, 'w', encoding='utf-8') as f:
                if str(save_path).endswith(('.yaml', '.yml')):
                    yaml.dump(self._settings, f, default_flow_style=False)
                else:
                    json.dump(self._settings, f, indent=2)
                    
            self._modified = False
            self._config_path = save_path
            self.logger.info(f"Settings saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save settings to {save_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting by key with dot notation
        
        Args:
            key: The setting key (e.g. 'app.debug')
            default: Default value if the key isn't found
            
        Returns:
            The setting value or the default
        """
        try:
            # Split the key by dots
            parts = key.split('.')
            value = self._settings
            
            # Navigate the nested dictionaries
            for part in parts:
                value = value[part]
                
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting by key with dot notation
        
        Args:
            key: The setting key (e.g. 'app.debug')
            value: The value to set
        """
        # Split the key by dots
        parts = key.split('.')
        current = self._settings
        
        # Navigate to the right level and create dictionaries if needed
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the value
        if parts[-1] in current and current[parts[-1]] == value:
            return  # No change needed
            
        current[parts[-1]] = value
        self._modified = True
        
        # Notify observers
        for callback in self._observers:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Error in settings observer: {e}")
    
    def has_key(self, key: str) -> bool:
        """
        Check if a setting exists
        
        Args:
            key: The setting key with dot notation
            
        Returns:
            bool: True if the setting exists
        """
        try:
            # Split the key by dots
            parts = key.split('.')
            current = self._settings
            
            # Navigate the nested dictionaries
            for part in parts:
                current = current[part]
                
            return True
        except (KeyError, TypeError):
            return False
    
    def reset(self, key: str = None) -> None:
        """
        Reset one or all settings to defaults
        
        Args:
            key: Key to reset (None for all settings)
        """
        if key is None:
            from . import defaults
            self._settings = copy.deepcopy(defaults.DEFAULT_CONFIG)
            self._modified = True
        else:
            # This is more complex, as we need the default for just this key
            from . import defaults
            try:
                default_value = self.get_from_dict(defaults.DEFAULT_CONFIG, key.split('.'))
                self.set(key, default_value)
            except (KeyError, TypeError):
                logger.warning(f"No default found for key: {key}")
    
    def register_observer(self, callback):
        """
        Register an observer to be notified when settings change
        
        Args:
            callback: Function that takes (key, value) arguments
        """
        if callback not in self._observers:
            self._observers.append(callback)
    
    def unregister_observer(self, callback):
        """
        Unregister a settings observer
        
        Args:
            callback: Previously registered callback function
        """
        if callback in self._observers:
            self._observers.remove(callback)
    
    def is_modified(self) -> bool:
        """
        Check if settings have been modified since last save
        
        Returns:
            bool: True if settings have been modified
        """
        return self._modified
    
    @staticmethod
    def get_from_dict(dictionary, key_parts):
        """
        Get a value from a nested dictionary using a list of keys
        
        Args:
            dictionary: The dictionary to navigate
            key_parts: List of keys to navigate the dictionary
            
        Returns:
            The value at the specified location
        
        Raises:
            KeyError: If the key doesn't exist
        """
        value = dictionary
        for part in key_parts:
            value = value[part]
        return value
    
    def _update_nested_dict(self, base_dict, new_dict):
        """
        Recursively update a nested dictionary
        
        Args:
            base_dict: The base dictionary to update
            new_dict: The dictionary with new values
        """
        for key, value in new_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                # Recursive update for nested dictionaries
                self._update_nested_dict(base_dict[key], value)
            else:
                # Simple update for non-dictionary values or new keys
                base_dict[key] = value
