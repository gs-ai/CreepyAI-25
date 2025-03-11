"""
CreepyAI Plugins Package

This package contains various plugins for the CreepyAI application.
Plugins provide extended functionality for collecting and analyzing location data.
"""
import os
import importlib
import logging
import sys
from typing import Dict, Any, List, Callable, Type

logger = logging.getLogger(__name__)

# Ensure plugins directory is in the Python path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

# Plugin adapter to ensure compatibility with different plugin formats
class PluginAdapter:
    """Adapter for different plugin formats to ensure compatibility with PluginManager"""
    
    @staticmethod
    def adapt(plugin_instance):
        """
        Adapt a plugin instance to ensure it has the necessary methods
        for compatibility with the PluginManager.
        
        Args:
            plugin_instance: The plugin instance to adapt
            
        Returns:
            The adapted plugin instance
        """
        # Ensure get_info method exists
        if not hasattr(plugin_instance, 'get_info'):
            plugin_instance.get_info = lambda: {
                "name": getattr(plugin_instance, 'name', getattr(plugin_instance, '__class__.__name__', 'Unknown')),
                "description": getattr(plugin_instance, 'description', 'No description'),
                "version": getattr(plugin_instance, 'version', '1.0.0'),
                "author": getattr(plugin_instance, 'author', 'Unknown')
            }
        
        # Ensure run method exists
        if not hasattr(plugin_instance, 'run'):
            if hasattr(plugin_instance, 'execute'):
                original_execute = plugin_instance.execute
                plugin_instance.run = original_execute
            elif hasattr(plugin_instance, 'process'):
                original_process = plugin_instance.process
                plugin_instance.run = original_process
            elif hasattr(plugin_instance, 'collect_locations'):
                # Special case for location collectors
                original_collect = plugin_instance.collect_locations
                plugin_instance.run = lambda target, *args, **kwargs: original_collect(target, *args, **kwargs)
            elif hasattr(plugin_instance, 'returnLocations'):
                # Legacy location collectors
                original_return = plugin_instance.returnLocations
                plugin_instance.run = lambda target, *args, **kwargs: original_return(
                    target, {'dateFrom': None, 'dateTo': None, **(kwargs or {})}
                )
            else:
                plugin_instance.run = lambda *args, **kwargs: None
                logger.warning(f"Plugin {plugin_instance.__class__.__name__} has no run/execute/process method")
        
        # Ensure configure method exists
        if not hasattr(plugin_instance, 'configure'):
            if hasattr(plugin_instance, 'setup'):
                plugin_instance.configure = plugin_instance.setup
            elif hasattr(plugin_instance, 'config'):
                plugin_instance.configure = plugin_instance.config
            elif hasattr(plugin_instance, 'isConfigured'):
                # Legacy configure method
                original_is_configured = plugin_instance.isConfigured
                plugin_instance.configure = lambda: original_is_configured()[0]
            else:
                plugin_instance.configure = lambda: True
            
        return plugin_instance

# Define plugin registry - singleton pattern
class PluginRegistry:
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.plugins = {}
        self.categories = {}
        self.hooks = {}
        self.capabilities = {}
    
    def register_plugin(self, name, plugin_instance, category='uncategorized'):
        """Register a plugin with the registry"""
        adapted_instance = PluginAdapter.adapt(plugin_instance)
        self.plugins[name] = adapted_instance
        self.categories[name] = category
        return adapted_instance
    
    def get_plugin(self, name):
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def get_plugins_by_category(self, category):
        """Get all plugins in a specific category"""
        return {name: plugin for name, plugin in self.plugins.items() 
                if self.categories.get(name) == category}
    
    def register_hook(self, plugin_name, hook_name, handler):
        """Register a hook handler"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append((plugin_name, handler))
    
    def invoke_hook(self, hook_name, *args, **kwargs):
        """Invoke all handlers for a given hook"""
        results = []
        for plugin_name, handler in self.hooks.get(hook_name, []):
            try:
                result = handler(*args, **kwargs)
                results.append((plugin_name, result))
            except Exception as e:
                logger.error(f"Error invoking hook {hook_name} in {plugin_name}: {e}", exc_info=True)
                results.append((plugin_name, None))
        return results

# Create global registry instance
registry = PluginRegistry.instance()

# Load plugins automatically
def load_plugin_categories():
    """Load all plugin categories and register them"""
    categories = ['social_media', 'location_services', 'data_extraction', 'tools', 'other']
    
    for category in categories:
        category_path = os.path.join(plugin_dir, category)
        if os.path.exists(category_path) and os.path.isdir(category_path):
            # Get python files in this category
            for file_name in os.listdir(category_path):
                if file_name.endswith('.py') and not file_name.startswith('__'):
                    plugin_name = file_name[:-3]  # Remove .py extension
                    try:
                        # Import the module
                        module = importlib.import_module(f"app.plugins.{category}.{plugin_name}")
                        
                        # Look for plugin class
                        if hasattr(module, 'Plugin'):
                            plugin_class = getattr(module, 'Plugin')
                            plugin_instance = plugin_class()
                            registry.register_plugin(plugin_name, plugin_instance, category)
                            logger.info(f"Loaded plugin {plugin_name} from {category}")
                        elif hasattr(module, plugin_name):
                            plugin_class = getattr(module, plugin_name)
                            if callable(plugin_class):
                                plugin_instance = plugin_class()
                                registry.register_plugin(plugin_name, plugin_instance, category)
                                logger.info(f"Loaded plugin {plugin_name} from {category}")
                    except Exception as e:
                        logger.error(f"Error loading plugin {plugin_name} from {category}: {e}", exc_info=True)

# Load all plugins when this module is imported
try:
    load_plugin_categories()
except Exception as e:
    logger.error(f"Error loading plugin categories: {e}", exc_info=True)
