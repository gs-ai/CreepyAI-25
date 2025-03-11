"""
Central configuration loader for CreepyAI.
Provides unified access to configuration from the consolidated directory.
"""
import os
import sys
import json
import yaml
import logging
from typing import Dict, Any, Optional, Union

# Get the app root directory
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# Add parent directory to path
sys.path.insert(0, APP_ROOT)

from configs.config_compat import get_config_path

logger = logging.getLogger('creepyai.configs.loader')

class ConfigLoader:
    """Centralized configuration loader that handles various file formats."""
    
    def __init__(self):
        """Initialize the configuration loader."""
        self.config_cache = {}
        self.app_root = APP_ROOT
        self.config_dir = CONFIG_DIR
    
    def get_config_file(self, name: str) -> Optional[str]:
        """Get the path to a configuration file.
        
        Args:
            name: Configuration file name or relative path
            
        Returns:
            Full path to the configuration file or None if not found
        """
        # Handle various config file extensions
        if '.' not in name:
            # Try common extensions
            for ext in ['.json', '.yaml', '.yml', '.conf']:
                path = get_config_path(name + ext)
                if os.path.exists(path):
                    return path
        else:
            # Direct path
            path = get_config_path(name)
            if os.path.exists(path):
                return path
                
        # Special case for plugin configs
        plugin_path = get_config_path(f"plugins/{name}")
        if os.path.exists(plugin_path):
            return plugin_path
            
        return None
    
    def load_config(self, name: str) -> Dict[str, Any]:
        """Load a configuration file by name.
        
        Args:
            name: Configuration file name or relative path
            
        Returns:
            Configuration data as dictionary
        """
        # Check cache first
        if name in self.config_cache:
            return self.config_cache[name]
            
        # Get file path
        file_path = self.get_config_file(name)
        if not file_path:
            logger.warning(f"Config file not found: {name}")
            return {}
            
        # Load based on file extension
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    config = json.load(f)
                elif file_path.endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(f) or {}
                else:
                    # Basic config parsing for .conf files
                    config = {}
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            
            # Cache and return
            self.config_cache[name] = config
            return config
            
        except Exception as e:
            logger.error(f"Error loading config {name}: {e}")
            return {}
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get the main application configuration.
        
        Returns:
            Application configuration dictionary
        """
        return self.load_config('app_config')
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin configuration dictionary
        """
        # Try several naming patterns
        for name in [
            f"plugins/{plugin_name}",
            f"plugins/{plugin_name}.conf",
            f"plugins/{plugin_name}.json",
            f"plugins/{plugin_name}.yaml"
        ]:
            config = self.load_config(name)
            if config:
                return config
                
        return {}
        
    def save_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Save configuration data to file.
        
        Args:
            name: Configuration file name or relative path
            config: Configuration data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine file path and format
            if '.' not in name:
                # Default to JSON for new files
                file_path = get_config_path(name + '.json')
            else:
                file_path = get_config_path(name)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save based on file extension
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    json.dump(config, f, indent=2)
                elif file_path.endswith(('.yaml', '.yml')):
                    yaml.safe_dump(config, f, default_flow_style=False)
                else:
                    # Simple format for .conf files
                    for key, value in config.items():
                        f.write(f"{key} = {value}\n")
            
            # Update cache
            self.config_cache[name] = config
            return True
            
        except Exception as e:
            logger.error(f"Error saving config {name}: {e}")
            return False

# Create singleton instance
config_loader = ConfigLoader()
