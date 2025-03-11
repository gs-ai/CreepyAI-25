"""
Plugin adapter for CreepyAI
"""
import inspect
import logging
import importlib
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class CreepyAIPluginAdapter:
    """
    Adapter class for CreepyAI plugins to ensure compatibility with PluginManager
    """
    def __init__(self, plugin_instance: Any):
        """
        Initialize the adapter with a plugin instance
        
        Args:
            plugin_instance: The plugin instance to adapt
        """
        self._plugin = plugin_instance
        self._name = getattr(plugin_instance, 'name', 
                            getattr(plugin_instance, '__class__.__name__', 'UnknownPlugin'))
        self._description = getattr(plugin_instance, 'description', 'No description provided')
        self._version = getattr(plugin_instance, 'version', '1.0.0')
        self._author = getattr(plugin_instance, 'author', 'Unknown')
        
        # Map plugin methods to standard interface
        self._map_methods()
    
    def _map_methods(self):
        """Map plugin methods to standard interface"""
        # Map run method
        if hasattr(self._plugin, 'run'):
            self.run = self._plugin.run
        elif hasattr(self._plugin, 'execute'):
            self.run = self._plugin.execute
        elif hasattr(self._plugin, 'process'):
            self.run = self._plugin.process
        else:
            # Create a dummy run method
            self.run = lambda *args, **kwargs: {
                "status": "error",
                "message": f"Plugin {self._name} does not have a run/execute/process method"
            }
        
        # Map configure method
        if hasattr(self._plugin, 'configure'):
            self.configure = self._plugin.configure
        elif hasattr(self._plugin, 'setup'):
            self.configure = self._plugin.setup
        elif hasattr(self._plugin, 'config'):
            self.configure = self._plugin.config
        else:
            # Create a dummy configure method
            self.configure = lambda: True
    
    def get_info(self) -> Dict[str, str]:
        """
        Get plugin information
        
        Returns:
            Dict with plugin info
        """
        if hasattr(self._plugin, 'get_info'):
            return self._plugin.get_info()
            
        return {
            "name": self._name,
            "description": self._description,
            "version": self._version,
            "author": self._author
        }
    
    @staticmethod
    def adapt_plugin(plugin_or_class: Any) -> 'CreepyAIPluginAdapter':
        """
        Static method to adapt a plugin instance or class
        
        Args:
            plugin_or_class: Plugin instance or class to adapt
            
        Returns:
            Adapted plugin instance
        """
        if inspect.isclass(plugin_or_class):
            try:
                instance = plugin_or_class()
                return CreepyAIPluginAdapter(instance)
            except Exception as e:
                logger.error(f"Error instantiating plugin class: {e}")
                raise
        else:
            return CreepyAIPluginAdapter(plugin_or_class)
