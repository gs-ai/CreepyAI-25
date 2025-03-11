"""
Plugin registry for CreepyAI
"""
import logging
from typing import Dict, List, Any, Callable

logger = logging.getLogger(__name__)

class PluginRegistry:
    """
    Registry for plugins, plugin capabilities, and hooks
    """
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        # Dictionary mapping plugin IDs to plugin instances
        self.plugins = {}
        
        # Dictionary mapping plugin IDs to categories
        self.categories = {}
        
        # Dictionary mapping hook names to a list of (plugin_id, handler) tuples
        self.hooks = {}
        
        # Dictionary mapping capability names to plugin IDs
        self.capabilities = {}
    
    def register_plugin(self, plugin_id: str, plugin_instance: Any, category: str = 'uncategorized'):
        """
        Register a plugin with the registry
        
        Args:
            plugin_id: ID of the plugin
            plugin_instance: The plugin instance
            category: Category of the plugin
        """
        self.plugins[plugin_id] = plugin_instance
        self.categories[plugin_id] = category
        
        logger.info(f"Registered plugin {plugin_id} in category {category}")
        
        return plugin_instance
    
    def get_plugin(self, plugin_id: str) -> Any:
        """
        Get a plugin by ID
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_id)
    
    def get_plugins_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all plugins in a specific category
        
        Args:
            category: Category to filter by
            
        Returns:
            Dictionary of plugin ID to plugin instance
        """
        return {
            plugin_id: plugin 
            for plugin_id, plugin in self.plugins.items() 
            if self.categories.get(plugin_id) == category
        }
    
    def register_hook(self, plugin_id: str, hook_name: str, handler: Callable):
        """
        Register a hook handler
        
        Args:
            plugin_id: ID of the plugin
            hook_name: Name of the hook
            handler: Hook handler function
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
            
        self.hooks[hook_name].append((plugin_id, handler))
        logger.info(f"Registered hook {hook_name} for plugin {plugin_id}")
    
    def invoke_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Invoke all handlers for a hook
        
        Args:
            hook_name: Name of the hook
            *args: Positional arguments to pass to the handlers
            **kwargs: Keyword arguments to pass to the handlers
            
        Returns:
            List of (plugin_id, result) tuples
        """
        results = []
        
        for plugin_id, handler in self.hooks.get(hook_name, []):
            try:
                result = handler(*args, **kwargs)
                results.append((plugin_id, result))
            except Exception as e:
                logger.error(f"Error invoking hook {hook_name} for plugin {plugin_id}: {e}")
                results.append((plugin_id, None))
                
        return results
    
    def register_capability(self, plugin_id: str, capability: str, description: str, metadata: Dict[str, Any] = None):
        """
        Register a plugin capability
        
        Args:
            plugin_id: ID of the plugin
            capability: Name of the capability
            description: Description of the capability
            metadata: Additional metadata about the capability
        """
        self.capabilities[capability] = {
            'plugin': plugin_id,
            'description': description,
            'metadata': metadata or {}
        }
        
        logger.info(f"Registered capability {capability} for plugin {plugin_id}")
    
    def get_plugin_with_capability(self, capability: str) -> Any:
        """
        Get a plugin that provides a specific capability
        
        Args:
            capability: The capability to look for
            
        Returns:
            Plugin instance or None if not found
        """
        if capability not in self.capabilities:
            return None
            
        plugin_id = self.capabilities[capability]['plugin']
        return self.get_plugin(plugin_id)

# Create singleton instance
registry = PluginRegistry.instance()
