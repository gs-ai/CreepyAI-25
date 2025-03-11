"""
Base plugin class for CreepyAI.
"""
import os
import sys
import logging
import datetime
import traceback
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass

logger = logging.getLogger('creepyai.plugins.base')

@dataclass
class LocationPoint:
    """Data class for location information"""
    latitude: float
    longitude: float
    timestamp: datetime.datetime
    source: str = "unknown"
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    context: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

class PluginError(Exception):
    """Base class for plugin errors"""
    pass

class ConfigurationError(PluginError):
    """Error raised when plugin configuration is invalid"""
    pass

class ExecutionError(PluginError):
    """Error raised when plugin execution fails"""
    pass

class PluginBase:
    """Base class for all CreepyAI plugins."""
    
    def __init__(self):
        """Initialize plugin."""
        self.name = self.__class__.__name__
        self.description = "Base plugin for CreepyAI"
        self.version = "1.0.0"
        self.author = "CreepyAI"
        self.enabled = True
        self.initialized = False
        
        # Get project root
        try:
            from app.core.config import Configuration
            self.config = Configuration()
            self.project_root = self.config.get_project_root()
        except ImportError:
            logger.warning("Could not load configuration, using relative paths")
            self.project_root = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", ".."
            ))
    
    def initialize(self) -> bool:
        """Initialize plugin.
        
        Returns:
            bool: True if initialization was successful
        """
        self.initialized = True
        return True
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Plugin execution result
        """
        logger.warning(f"Plugin {self.name} does not implement execute()")
        return None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata.
        
        Returns:
            Dict[str, Any]: Plugin metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled
        }
    
    def get_config(self, key: str = None, default: Any = None) -> Any:
        """Get plugin configuration.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        # Try to load plugin configuration
        try:
            from app.plugins.plugin_utils import get_plugin_config_path
            import json
            
            config_path = get_plugin_config_path(self.name)
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if key is None:
                    return config
                return config.get(key, default)
        except Exception as e:
            logger.error(f"Error loading plugin configuration: {e}")
        
        return default
