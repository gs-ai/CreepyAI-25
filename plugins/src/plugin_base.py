"""
Base plugin interface for CreepyAI plugins.
All plugins should inherit from the BasePlugin class.
"""

import abc
from typing import List, Dict, Any, Tuple, Optional

class BasePlugin(abc.ABC):
    """Base class for all CreepyAI plugins."""
    
    def __init__(self, config=None):
        """
        Initialize plugin with optional configuration
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._name = "Base Plugin"
        self._version = "1.0.0"
        self._description = "Base plugin class"
    
    @property
    def name(self) -> str:
        """Get plugin name"""
        return self._name
        
    @property
    def version(self) -> str:
        """Get plugin version"""
        return self._version
        
    @property
    def description(self) -> str:
        """Get plugin description"""
        return self._description
        
    def get_version(self) -> str:
        """Get plugin version"""
        return self._version
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self._config
        
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Update plugin configuration
        
        Args:
            config: New configuration dictionary
        """
        self._config = config
    
    def is_configured(self) -> Tuple[bool, str]:
        """
        Check if plugin is properly configured
        
        Returns:
            Tuple of (is_configured, message)
        """
        return True, "Plugin ready"
    
    def supports_args(self) -> bool:
        """Check if plugin supports additional arguments"""
        return False
    
    @abc.abstractmethod
    def search(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute search for target
        
        Args:
            target: Search target
            **kwargs: Additional search parameters
            
        Returns:
            List of results
        """
        pass
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate plugin integrity
        
        Returns:
            Tuple of (is_valid, message)
        """
        return True, "Plugin is valid"
    
    def cleanup(self) -> None:
        """Perform cleanup operations"""
        pass
