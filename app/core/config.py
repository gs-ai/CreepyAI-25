"""
Configuration management for CreepyAI.
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger('creepyai.core.config')

class Configuration:
    """Configuration class for managing application settings."""
    
    _instance = None
    _project_root = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize configuration with default values."""
        self.config = get_default_config()
        self.config_path = None
        self.loaded = False
        # Set project root
        self._project_root = self._get_project_root()

    @staticmethod
    def _get_project_root():
        """Get the project root directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up from app.core to project root
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        return project_root
        
    def get_project_root(self):
        """Return the project root directory."""
        return self._project_root
    
    def load(self, config_path: str) -> bool:
        """Load configuration from specified path.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        # Resolve path relative to project root if not absolute
        if not os.path.isabs(config_path):
            config_path = os.path.join(self._project_root, config_path)
            
        success, loaded_config = load_config(config_path)
        if success:
            self.config = loaded_config
            self.config_path = config_path
            self.loaded = True
            return True
        return False
    
    def get(self, section: str = None, key: str = None, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if section or key not found
            
        Returns:
            Configuration value or default if not found
        """
        if section is None:
            return self.config
            
        if section not in self.config:
            return default
            
        if key is None:
            return self.config[section]
            
        return self.config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
    
    def save(self, config_path: str = None) -> bool:
        """Save configuration to file.
        
        Args:
            config_path: Path to save configuration file, uses loaded path if None
            
        Returns:
            True if successful, False otherwise
        """
        path = config_path or self.config_path
        if not path:
            logger.error("No configuration path specified for saving")
            return False
            
        return save_config(self.config, path)

def load_config(config_path: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Tuple containing success status and configuration dict
    """
    try:
        # Get absolute path if config_path is relative
        if not os.path.isabs(config_path):
            # Use Configuration class to get project root
            project_root = Configuration()._project_root
            config_path = os.path.join(project_root, config_path)
            
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return False, get_default_config()
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        logger.info(f"Loaded configuration from {config_path}")
        return True, config
        
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return False, get_default_config()

def get_default_config() -> Dict[str, Any]:
    """Get default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "application": {
            "name": "CreepyAI",
            "version": "2.5.0",
            "debug": False,
            "theme": "system"
        },
        "ui": {
            "maximize_on_start": False,
            "remember_window_size": True,
            "window_width": 1200,
            "window_height": 800
        },
        "plugins": {
            "enabled": True,
            "auto_load": True,
            "user_plugins_path": ""
        },
        "map": {
            "default_zoom": 13,
            "default_latitude": 40.7128,
            "default_longitude": -74.0060,
            "tile_provider": "OpenStreetMap"
        },
        "logging": {
            "level": "INFO",
            "file_logging": True,
            "max_log_files": 10
        }
    }

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get absolute path if config_path is relative
        if not os.path.isabs(config_path):
            # Use Configuration class to get project root
            project_root = Configuration()._project_root
            config_path = os.path.join(project_root, config_path)
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
        logger.info(f"Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False
