"""
Base plugin class for CreepyAI plugins.
"""
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger('creepyai.plugins.base')

class BasePlugin:
    """Base class for all CreepyAI plugins."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.name = self.__class__.__name__
        self.description = "Base CreepyAI plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.enabled = True
        self.initialized = False
        
        # Get project root from Configuration
        from app.core.config import Configuration
        self.config = Configuration()
        self.project_root = self.config.get_project_root()
        
        logger.debug(f"Initialized base plugin: {self.name}")
    
    def initialize(self) -> bool:
        """Initialize the plugin.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
        
        self.initialized = True
        logger.info(f"Initialized plugin: {self.name}")
        return True
    
    def get_name(self) -> str:
        """Get the name of the plugin.
        
        Returns:
            str: Plugin name
        """
        return self.name
    
    def get_description(self) -> str:
        """Get the description of the plugin.
        
        Returns:
            str: Plugin description
        """
        return self.description
    
    def get_version(self) -> str:
        """Get the version of the plugin.
        
        Returns:
            str: Plugin version
        """
        return self.version
    
    def get_author(self) -> str:
        """Get the author of the plugin.
        
        Returns:
            str: Plugin author
        """
        return self.author
    
    def is_enabled(self) -> bool:
        """Check if the plugin is enabled.
        
        Returns:
            bool: True if the plugin is enabled, False otherwise
        """
        return self.enabled
    
    def enable(self) -> bool:
        """Enable the plugin.
        
        Returns:
            bool: True if the plugin was enabled successfully, False otherwise
        """
        self.enabled = True
        logger.info(f"Enabled plugin: {self.name}")
        return True
    
    def disable(self) -> bool:
        """Disable the plugin.
        
        Returns:
            bool: True if the plugin was disabled successfully, False otherwise
        """
        self.enabled = False
        logger.info(f"Disabled plugin: {self.name}")
        return True
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin functionality.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        
        Returns:
            Any: Result of the plugin execution
        """
        logger.warning(f"Plugin {self.name} does not implement execute()")
        return None

# Plugin class that other modules can import
class Plugin(BasePlugin):
    """Default plugin implementation."""
    
    def __init__(self):
        super().__init__()
        self.name = "DefaultPlugin"
        self.description = "Default plugin implementation"
