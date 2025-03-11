"""
Plugin Manager for CreepyAI
"""
import os
import sys
import logging
import importlib.util
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Unified plugin manager for CreepyAI that works with both PyQt5 and Tkinter
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern to get the plugin manager instance"""
        if cls._instance is None:
            cls._instance = PluginManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the plugin manager"""
        # Don't re-initialize if this is a singleton instance
        if PluginManager._instance is not None:
            return
            
        self.plugins = {}
        self.plugin_paths = []
        self.loaded = False
        self._plugin_cache = {}  # Cache for plugin instances
    
    def set_plugin_paths(self, paths: List[str]):
        """Set the plugin paths to search for plugins"""
        self.plugin_paths = paths
        self.loaded = False
        # Clear cache when paths change
        self._plugin_cache.clear()
    
    @lru_cache(maxsize=32)  # Cache plugin discovery results
    def discover_plugins(self) -> Dict[str, Any]:
        """
        Discover available plugins in the plugin paths
        
        Returns:
            Dict[str, Any]: Dictionary of plugin information
        """
        if self.loaded:
            return self.plugins
            
        self.plugins = {}
        
        # Ensure the plugins directory is in sys.path
        for path in self.plugin_paths:
            if path not in sys.path and os.path.exists(path):
                sys.path.append(path)
        
        for plugin_dir in self.plugin_paths:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
                
            logger.info(f"Searching for plugins in: {plugin_dir}")
            
            # Check for Python files in the directory
            for filename in os.listdir(plugin_dir):
                if not filename.endswith('_plugin.py') and not filename.endswith('Plugin.py'):
                    continue
                    
                plugin_path = os.path.join(plugin_dir, filename)
                plugin_name = os.path.splitext(filename)[0]
                
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                    if spec is None or spec.loader is None:
                        logger.warning(f"Could not load plugin spec: {plugin_path}")
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for plugin class (expect Plugin or InputPlugin suffix)
                    plugin_class_name = None
                    for name in dir(module):
                        if name.endswith('Plugin') and name != 'InputPlugin' and name != 'Plugin':
                            plugin_class_name = name
                            break
                            
                    if not plugin_class_name:
                        logger.warning(f"No plugin class found in {plugin_path}")
                        continue
                        
                    # Get the plugin class
                    plugin_class = getattr(module, plugin_class_name)
                    
                    # Create instance and store it
                    plugin_instance = plugin_class()
                    
                    # Use getName or plugin_name attribute if available
                    if hasattr(plugin_instance, 'getName'):
                        name = plugin_instance.getName()
                    elif hasattr(plugin_instance, 'plugin_name'):
                        name = plugin_instance.plugin_name
                    else:
                        name = plugin_name
                        
                    self.plugins[name] = {
                        'name': name,
                        'path': plugin_path,
                        'instance': plugin_instance,
                        'module': module,
                        'description': getattr(plugin_instance, 'description', ''),
                        'version': getattr(plugin_instance, 'version', '1.0.0'),
                        'author': getattr(plugin_instance, 'author', 'Unknown')
                    }
                    
                    logger.info(f"Loaded plugin: {name} v{self.plugins[name]['version']}")
                except Exception as e:
                    logger.error(f"Error loading plugin {plugin_path}: {str(e)}")
                    logger.debug(f"Exception details:", exc_info=True)
        
        self.loaded = True
        return self.plugins
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """
        Get a plugin by name
        
        Args:
            name (str): Plugin name
        
        Returns:
            Optional[Any]: Plugin instance or None if not found
        """
        if not self.loaded:
            self.discover_plugins()
            
        # Use cache if available
        if name in self._plugin_cache:
            return self._plugin_cache[name]
            
        plugin_data = self.plugins.get(name)
        if plugin_data:
            self._plugin_cache[name] = plugin_data['instance']
            return plugin_data['instance']
            
        return None
        
    def get_plugin_names(self) -> List[str]:
        """
        Get a list of all plugin names
        
        Returns:
            List[str]: List of plugin names
        """
        if not self.loaded:
            self.discover_plugins()
            
        return list(self.plugins.keys())
        
    def run_plugin(self, name: str, method: str, *args, **kwargs) -> Any:
        """
        Run a plugin method with the given arguments
        
        Args:
            name (str): Plugin name
            method (str): Method name to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Return value from the plugin method
        """
        plugin = self.get_plugin(name)
        if not plugin:
            logger.error(f"Plugin not found: {name}")
            return None
            
        if not hasattr(plugin, method):
            logger.error(f"Method not found in plugin {name}: {method}")
            return None
            
        try:
            method_to_call = getattr(plugin, method)
            return method_to_call(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error running plugin {name}.{method}: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return None
    
    def get_input_plugins(self) -> List[Any]:
        """
        Get all input plugins
        
        Returns:
            List[Any]: List of input plugin instances
        """
        plugins = self.discover_plugins()
        return [p['instance'] for p in plugins.values() 
                if hasattr(p['instance'], 'returnLocations')]
