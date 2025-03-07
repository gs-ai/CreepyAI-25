"""
Configuration Manager for CreepyAI
"""
import os
import json
import logging
import sys
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration for both PyQt5 and Tkinter versions of CreepyAI
    """
    
    def __init__(self):
        """Initialize the configuration manager"""
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config = self.load_config()
        
    def _get_config_dir(self) -> str:
        """Get the configuration directory based on the platform"""
        if sys.platform == 'darwin':  # macOS
            config_dir = os.path.expanduser("~/.config/creepyai")
        elif sys.platform == 'win32':  # Windows
            config_dir = os.path.expanduser("~/AppData/Local/CreepyAI")
        else:  # Linux and others
            config_dir = os.path.expanduser("~/.local/share/creepyai")
            
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "ui_preference": "auto",  # 'pyqt5', 'tkinter', or 'auto'
            "output_directory": os.path.expanduser("~/Documents/CreepyAI"),
            "plugins_directory": os.path.join(self.config_dir, "plugins"),
            "api_keys": {},
            "check_updates": True,
            "plugins": {
                "enabled": [],
                "disabled": []
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Update with any missing keys from default
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                        
                return config
            else:
                # Create default config
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file"""
        if config is not None:
            self.config = config
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value"""
        self.config[key] = value
        return self.save_config()
    
    def get_ui_preference(self) -> str:
        """Get the preferred UI"""
        preference = self.get("ui_preference", "auto")
        
        if preference == "auto":
            # Auto-detect based on available libraries
            try:
                import tkinter
                return "tkinter"
            except ImportError:
                try:
                    from PyQt5 import QtCore
                    return "pyqt5"
                except ImportError:
                    return "cli"  # Fallback to command-line interface
        else:
            return preference
    
    def get_plugin_directories(self) -> list:
        """Get all plugin directories"""
        plugin_dirs = [
            os.path.join(os.getcwd(), 'plugins'),
            self.get("plugins_directory")
        ]
        return plugin_dirs
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled"""
        enabled_plugins = self.get("plugins", {}).get("enabled", [])
        disabled_plugins = self.get("plugins", {}).get("disabled", [])
        
        if plugin_name in disabled_plugins:
            return False
        if plugin_name in enabled_plugins:
            return True
            
        # Default to enabled if not explicitly disabled
        return True
    
    def set_plugin_enabled(self, plugin_name: str, enabled: bool) -> bool:
        """Enable or disable a plugin"""
        plugins = self.get("plugins", {})
        
        if "enabled" not in plugins:
            plugins["enabled"] = []
        if "disabled" not in plugins:
            plugins["disabled"] = []
            
        # Update the lists
        if enabled:
            if plugin_name in plugins["disabled"]:
                plugins["disabled"].remove(plugin_name)
            if plugin_name not in plugins["enabled"]:
                plugins["enabled"].append(plugin_name)
        else:
            if plugin_name in plugins["enabled"]:
                plugins["enabled"].remove(plugin_name)
            if plugin_name not in plugins["disabled"]:
                plugins["disabled"].append(plugin_name)
                
        # Update config
        self.set("plugins", plugins)
        return True
    
    def create_project_directory(self, project_name: str) -> str:
        """Create project directory and return its path"""
        output_dir = self.get("output_directory")
        project_dir = os.path.join(output_dir, project_name)
        
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
