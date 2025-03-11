"""
Plugin management for CreepyAI.
Unified plugin manager implementation.
"""
import os
import sys
import glob
import yaml
import logging
import importlib.util
from typing import Dict, List, Any, Optional

logger = logging.getLogger('creepyai.utilities.PluginManager')

class PluginManager:
    """Manager for loading and handling plugins."""
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins = {}
        self.plugin_configs = {}
        self.plugin_paths = []
        self.enabled = True
        self.initialized = False
        
        # Initialize configuration
        from app.core.config import Configuration
        self.config = Configuration()
        self.project_root = self.config.get_project_root()
        
        # Default plugin paths
        self.plugin_paths = [
            os.path.join(self.project_root, 'plugins', 'src'),
            os.path.join(self.project_root, 'src', 'plugins')
        ]
        
        # Check if plugins are enabled in config
        plugins_config = self.config.get('plugins')
        if plugins_config:
            self.enabled = plugins_config.get('enabled', True)
            user_plugins_path = plugins_config.get('user_plugins_path', '')
            if user_plugins_path:
                # Add user-defined plugin path if specified
                if os.path.isabs(user_plugins_path):
                    self.plugin_paths.append(user_plugins_path)
                else:
                    self.plugin_paths.append(os.path.join(self.project_root, user_plugins_path))
        
        # Load plugin configuration file if exists
        self._load_plugin_config()
        
        logger.info("Plugin manager initialized")
    
    def _load_plugin_config(self):
        """Load plugin configuration from yaml file."""
        config_paths = [
            os.path.join(self.project_root, 'plugins', 'plugins.yaml'),
            os.path.join(self.project_root, 'configs', 'plugins', 'plugins.yaml')
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f)
                        logger.info(f"Loaded plugin configuration from {path}")
                        
                        # Process plugin configuration
                        if isinstance(config, dict):
                            # Add plugin paths from config
                            if 'plugin_paths' in config and isinstance(config['plugin_paths'], list):
                                for p in config['plugin_paths']:
                                    if os.path.isabs(p):
                                        self.plugin_paths.append(p)
                                    else:
                                        self.plugin_paths.append(os.path.join(self.project_root, p))
                            
                            # Store enabled plugins
                            if 'enabled_plugins' in config and isinstance(config['enabled_plugins'], list):
                                self.enabled_plugins = config['enabled_plugins']
                            else:
                                self.enabled_plugins = []
                                
                        return True
                except Exception as e:
                    logger.error(f"Error loading plugin configuration from {path}: {e}")
        
        logger.warning(f"Plugin config file not found in any standard location")
        # Create default plugin config
        self._create_default_plugin_config()
        return False
    
    def _create_default_plugin_config(self):
        """Create a default plugin configuration file."""
        try:
            config = {
                'enabled_plugins': [],
                'plugin_paths': ['plugins/src']
            }
            
            config_dir = os.path.join(self.project_root, 'plugins')
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = os.path.join(config_dir, 'plugins.yaml')
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            logger.info(f"Created default plugin configuration at {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating default plugin configuration: {e}")
            return False
    
    def load_plugins(self) -> bool:
        """Load all available plugins.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("Plugins are disabled in configuration")
            return False
            
        if not self.plugin_paths:
            logger.warning("No plugin paths configured")
            return False
        
        success = True
        loaded_count = 0
        
        for path in self.plugin_paths:
            if os.path.exists(path) and os.path.isdir(path):
                logger.info(f"Scanning for plugins in: {path}")
                try:
                    # Look for Python files in the plugin directory
                    for item in os.listdir(path):
                        plugin_path = os.path.join(path, item)
                        if item.endswith('.py') and os.path.isfile(plugin_path):
                            if self._load_plugin_from_file(plugin_path):
                                loaded_count += 1
                        elif os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                            if self._load_plugin_from_directory(plugin_path):
                                loaded_count += 1
                except Exception as e:
                    logger.error(f"Error loading plugins from {path}: {e}")
                    success = False
            else:
                logger.warning(f"Plugin path does not exist or is not a directory: {path}")
                
        logger.info(f"Loaded {loaded_count} plugins")
        self.initialized = True
        return success and loaded_count > 0
    
    def _load_plugin_from_file(self, plugin_path: str) -> bool:
        """Load a plugin from a Python file.
        
        Args:
            plugin_path: Path to plugin file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            module_name = os.path.basename(plugin_path)[:-3]  # Remove .py extension
            logger.debug(f"Loading plugin module: {module_name} from {plugin_path}")
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load plugin spec: {plugin_path}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for a Plugin class
            if hasattr(module, 'Plugin'):
                plugin_class = getattr(module, 'Plugin')
                plugin = plugin_class()
                self.plugins[module_name] = plugin
                logger.info(f"Successfully loaded plugin: {module_name}")
                return True
            else:
                logger.warning(f"No Plugin class found in {plugin_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    def _load_plugin_from_directory(self, plugin_dir: str) -> bool:
        """Load a plugin from a directory.
        
        Args:
            plugin_dir: Path to plugin directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            module_name = os.path.basename(plugin_dir)
            logger.debug(f"Loading plugin package: {module_name} from {plugin_dir}")
            
            # Import the module
            if plugin_dir not in sys.path:
                sys.path.append(os.path.dirname(plugin_dir))
            
            module = importlib.import_module(module_name)
            
            # Look for a Plugin class
            if hasattr(module, 'Plugin'):
                plugin_class = getattr(module, 'Plugin')
                plugin = plugin_class()
                self.plugins[module_name] = plugin
                logger.info(f"Successfully loaded plugin package: {module_name}")
                return True
            else:
                logger.warning(f"No Plugin class found in {plugin_dir}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading plugin package {plugin_dir}: {e}")
            return False
    
    def get_plugins(self) -> Dict[str, Any]:
        """Get all loaded plugins.
        
        Returns:
            Dict[str, Any]: Dictionary of plugin name to plugin instance
        """
        return self.plugins
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a specific plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Optional[Any]: Plugin instance or None if not found
        """
        return self.plugins.get(name)
    
    def initialize(self) -> bool:
        """Initialize the plugin manager and load plugins.
        
        Returns:
            bool: True if initialization was successful
        """
        if not self.enabled:
            logger.info("Plugin system is disabled in configuration")
            return False
            
        # Load plugins
        success = self.load_plugins()
        
        # Mark as initialized
        self.initialized = True
        return success
