import os
import sys
import importlib.util
import logging
from creepy.plugins.base_plugin import BasePlugin  # Adjust the import path as necessary

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.plugins = []

    # ...existing code...

    def load_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'creepy', 'plugins')
        sys.path.insert(0, plugin_dir)
        logger.info(f"Looking for plugins in: {plugin_dir}")
        for filename in os.listdir(plugin_dir):
            if filename.endswith('_plugin.py'):
                plugin_name = filename[:-3]
                logger.info(f"Found plugin: {plugin_name}")
                self._import_plugin(plugin_name)

    def _import_plugin(self, plugin_name):
        try:
            spec = importlib.util.find_spec(plugin_name)
            if spec is None:
                logger.error(f"Cannot find spec for {plugin_name}")
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugin_class = attr
                    break
            if plugin_class:
                plugin_instance = plugin_class()
                self.plugins.append(plugin_instance)
                logger.info(f"Successfully imported {plugin_name}")
            else:
                logger.error(f"Plugin class not found in {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to import {plugin_name}: {e}")

    def initialize_plugin(self, plugin_name):
        # Method to initialize a specific plugin
        pass

    def get_plugin(self, plugin_name):
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None

    def get_all_plugins(self):
        return self.plugins

    # ...existing code...
