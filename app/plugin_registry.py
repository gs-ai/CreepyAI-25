"""
Plugin Registry for CreepyAI
Handles registration and loading of all plugins
"""

import logging
from typing import List, Type
from app.plugins.base_plugin import BasePlugin

# Import plugin categories
from app.plugins.social_media import plugins as social_media_plugins

logger = logging.getLogger(__name__)

def register_plugins() -> List[Type[BasePlugin]]:
    """
    Register all available plugins from different categories
    Returns a list of plugin classes that can be instantiated
    """
    all_plugins = []
    
    # Register social media plugins
    try:
        all_plugins.extend(social_media_plugins)
        logger.info(f"Registered {len(social_media_plugins)} social media plugins")
    except Exception as e:
        logger.error(f"Error registering social media plugins: {e}")
    
    # Here you would register plugins from other categories (future expansion)
    # ...
    
    return all_plugins

def instantiate_plugins() -> List[BasePlugin]:
    """
    Create instances of all registered plugins
    """
    plugin_classes = register_plugins()
    plugin_instances = []
    
    for plugin_class in plugin_classes:
        try:
            plugin = plugin_class()
            plugin_instances.append(plugin)
            logger.debug(f"Instantiated plugin: {plugin.name}")
        except Exception as e:
            logger.error(f"Failed to instantiate plugin {plugin_class.__name__}: {e}")
    
    return plugin_instances

def get_plugin_by_name(name: str) -> BasePlugin:
    """
    Get plugin instance by name
    """
    plugins = instantiate_plugins()
    for plugin in plugins:
        if plugin.name == name:
            return plugin
    return None
