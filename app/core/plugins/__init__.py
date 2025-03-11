"""
CreepyAI Plugin System
"""
import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages loading and running of CreepyAI plugins"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_dirs = []
        self.categories = {}
        
        # Standard directories to look for plugins
        self.add_plugin_directory(os.path.join(os.path.dirname(__file__), 'standard'))
        
        # Add the main plugins directory
        app_plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../app/plugins'))
        self.add_plugin_directory(app_plugins_dir)
        
        # Add plugin category directories - scan depth-first to prioritize categorized plugins
        for category in ['social_media', 'location_services', 'data_extraction', 'tools', 'other']:
            category_dir = os.path.join(app_plugins_dir, category)
            if os.path.exists(category_dir) and os.path.isdir(category_dir):
                self.add_plugin_directory(category_dir)
        
        # User plugins directory
        user_plugins_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'plugins')
        self.add_plugin_directory(user_plugins_dir)
    
    def add_plugin_directory(self, directory):
        """Add a directory to search for plugins"""
        if os.path.exists(directory) and os.path.isdir(directory):
            if directory not in self.plugin_dirs:
                self.plugin_dirs.append(directory)
                # Make sure directory is in Python path
                if directory not in sys.path:
                    sys.path.insert(0, directory)
                return True
        else:
            # Create the directory if it doesn't exist
            try:
                os.makedirs(directory, exist_ok=True)
                self.plugin_dirs.append(directory)
                if directory not in sys.path:
                    sys.path.insert(0, directory)
                return True
            except Exception as e:
                logger.error(f"Failed to create plugin directory {directory}: {e}")
        return False
    
    def discover_plugins(self):
        """Discover all available plugins in the plugin directories"""
        # Clear existing plugins to avoid duplicates
        self.plugins = {}
        self.categories = {}
        
        for plugin_dir in self.plugin_dirs:
            category = self._get_category_from_path(plugin_dir)
            self._scan_directory(plugin_dir, category)
        
        logger.info(f"Discovered {len(self.plugins)} plugins across {len(set(self.categories.values()))} categories")
        return self.plugins
    
    def _get_category_from_path(self, path):
        """Determine plugin category from path"""
        path_parts = Path(path).parts
        
        # Check for category in path
        for part in path_parts:
            if part in ['social_media', 'location_services', 'data_extraction', 'tools', 'other']:
                return part
        
        # Check if it's in the standard directory
        if 'standard' in path_parts:
            return 'standard'
        
        # Default to uncategorized
        return 'uncategorized'
    
    def _scan_directory(self, directory, category='uncategorized'):
        """Scan a directory for plugin modules"""
        if not os.path.exists(directory):
            return
            
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Skip __pycache__ and dot files
            if item.startswith('.') or item == '__pycache__':
                continue
                
            if os.path.isdir(item_path):
                # Check if this is a plugin package (has __init__.py)
                if os.path.exists(os.path.join(item_path, '__init__.py')):
                    self._load_plugin_from_package(item, item_path, category)
                else:
                    # Recursively scan subdirectories with same category
                    self._scan_directory(item_path, category)
            elif item.endswith('.py') and not item.startswith('__'):
                # Load single-file plugin
                plugin_name = item[:-3]  # Remove .py extension
                self._load_plugin_from_file(plugin_name, item_path, category)
    
    def _load_plugin_from_package(self, name, path, category='uncategorized'):
        """Load a plugin from a package directory"""
        try:
            module_name = name
            spec = importlib.util.spec_from_file_location(
                module_name, os.path.join(path, '__init__.py')
            )
            if not spec:
                logger.warning(f"Failed to load plugin package {name} from {path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has a Plugin class or function
            if hasattr(module, 'Plugin'):
                plugin_class = getattr(module, 'Plugin')
                plugin_instance = plugin_class()
                self.plugins[name] = plugin_instance
                logger.info(f"Loaded plugin {name} from package {path}")
            elif hasattr(module, 'register_plugin'):
                register_func = getattr(module, 'register_plugin')
                plugin_instance = register_func()
                self.plugins[name] = plugin_instance
                logger.info(f"Registered plugin {name} from package {path}")
            else:
                logger.warning(f"Plugin package {name} lacks Plugin class or register_plugin function")
            
            # Additional code to track category
            if name in self.plugins:
                self.categories[name] = category
            
        except Exception as e:
            logger.error(f"Error loading plugin package {name}: {e}", exc_info=True)
    
    def _load_plugin_from_file(self, name, path, category='uncategorized'):
        """Load a plugin from a single Python file"""
        try:
            module_name = name
            spec = importlib.util.spec_from_file_location(module_name, path)
            if not spec:
                logger.warning(f"Failed to load plugin file {name} from {path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Try different patterns to find the plugin class or instance
            plugin_instance = None
            
            # Pattern 1: Class named 'Plugin'
            if hasattr(module, 'Plugin'):
                plugin_class = getattr(module, 'Plugin')
                if callable(plugin_class):  # It's a class
                    plugin_instance = plugin_class()
                    logger.info(f"Loaded plugin {name} from file {path} (Plugin class)")
            
            # Pattern 2: register_plugin function
            elif hasattr(module, 'register_plugin'):
                register_func = getattr(module, 'register_plugin')
                plugin_instance = register_func()
                logger.info(f"Loaded plugin {name} from file {path} (register_plugin function)")
            
            # Pattern 3: Class named same as file
            elif hasattr(module, name):
                plugin_class = getattr(module, name)
                if callable(plugin_class):  # It's a class
                    plugin_instance = plugin_class()
                    logger.info(f"Loaded plugin {name} from file {path} (named class)")
            
            # Pattern 4: BasePlugin or InputPlugin inheritance
            else:
                # Look for classes that inherit from BasePlugin or InputPlugin
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr.__module__ == module.__name__:
                        # Check if it inherits from BasePlugin or InputPlugin
                        base_names = [base.__name__ for base in attr.__mro__]
                        if 'BasePlugin' in base_names or 'InputPlugin' in base_names:
                            plugin_instance = attr()
                            logger.info(f"Loaded plugin {name} from file {path} (inheritance)")
                            break
            
            # If we found a plugin instance, store it
            if plugin_instance:
                self.plugins[name] = plugin_instance
                self.categories[name] = category
                
                # Ensure it has required methods
                self._ensure_required_methods(plugin_instance)
                
                return True
            else:
                logger.warning(f"No plugin class/instance found in {path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading plugin file {name}: {e}", exc_info=True)
            return False
    
    def _ensure_required_methods(self, plugin_instance):
        """Ensure the plugin instance has all required methods"""
        # Minimal methods required by our system
        if not hasattr(plugin_instance, 'get_info'):
            plugin_instance.get_info = lambda: {
                "name": getattr(plugin_instance, 'name', 'Unknown Plugin'),
                "description": getattr(plugin_instance, 'description', 'No description available'),
                "version": getattr(plugin_instance, 'version', '1.0.0'),
                "author": getattr(plugin_instance, 'author', 'Unknown')
            }
        
        if not hasattr(plugin_instance, 'run'):
            # Try to map to other common method names
            if hasattr(plugin_instance, 'execute'):
                plugin_instance.run = plugin_instance.execute
            elif hasattr(plugin_instance, 'process'):
                plugin_instance.run = plugin_instance.process
            else:
                # Create default implementation
                plugin_instance.run = lambda *args, **kwargs: {"error": "Method not implemented"}
    
    def get_plugin(self, name):
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def get_all_plugins(self):
        """Get all discovered plugins"""
        return self.plugins
    
    def get_plugins_by_category(self, category):
        """Get all plugins in a specific category"""
        return {name: plugin for name, plugin in self.plugins.items() 
                if self.categories.get(name) == category}
    
    def get_categories(self):
        """Get all available plugin categories"""
        return set(self.categories.values())
    
    def get_category(self, plugin_name):
        """Get the category of a specific plugin"""
        return self.categories.get(plugin_name, 'uncategorized')
    
    def run_plugin(self, name, *args, **kwargs):
        """Run a plugin by name"""
        plugin = self.get_plugin(name)
        if plugin and hasattr(plugin, 'run'):
            try:
                return plugin.run(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error running plugin {name}: {e}", exc_info=True)
                return None
        return None
