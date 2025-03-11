"""
Plugin Manager for CreepyAI
Manages loading and execution of plugins
"""

import os
import logging
from typing import List, Dict, Any, Optional

from app.plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages loading and execution of plugins"""
    
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, BasePlugin] = {}
    
    def load_plugins(self):
        """Load all plugins from the plugin directory"""
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]
                try:
                    module = __import__(f"app.plugins.{plugin_name}", fromlist=[plugin_name])
                    plugin_class = getattr(module, plugin_name.capitalize())
                    plugin_instance = plugin_class()
                    self.plugins[plugin_name] = plugin_instance
                    logger.info(f"Loaded plugin: {plugin_name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_name}: {e}")
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def execute_plugin(self, name: str, *args, **kwargs) -> Any:
        """Execute a plugin by name"""
        plugin = self.get_plugin(name)
        if plugin:
            return plugin.run(*args, **kwargs)
        else:
            logger.error(f"Plugin {name} not found")
            return None
