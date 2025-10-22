"""
Plugin management for CreepyAI.
Unified plugin manager implementation.
"""
import os
import yaml
import logging
from typing import Dict, List, Any, Optional

from app.plugins.catalog import PluginCatalog, PluginDescriptor

logger = logging.getLogger('creepyai.utilities.PluginManager')

class PluginManager:
    """Manager for loading and handling plugins."""
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, Any] = {}
        self.plugin_configs: Dict[str, Any] = {}
        self.plugin_paths: List[str] = []
        self.enabled = True
        self.initialized = False
        self.failed_plugins: Dict[str, str] = {}
        self.enabled_plugins: List[str] = []
        self._aliases: Dict[str, str] = {}
        self._catalog: Optional[PluginCatalog] = None
        self._descriptors: Dict[str, PluginDescriptor] = {}
        
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
    
    def load_plugins(self, *, force_refresh: bool = False) -> bool:
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

        prepared_paths = []
        for path in self.plugin_paths:
            try:
                os.makedirs(path, exist_ok=True)
                prepared_paths.append(path)
            except Exception as exc:
                logger.error(f"Unable to prepare plugin path {path}: {exc}")

        if not prepared_paths:
            logger.warning("No usable plugin roots available")
            return False

        try:
            catalog = PluginCatalog(prepared_paths)
        except ValueError as exc:
            logger.error("Failed to initialize plugin catalog: %s", exc)
            return False

        descriptors = catalog.load(force_refresh=force_refresh)
        allowed = {name.lower() for name in self.enabled_plugins} if self.enabled_plugins else None

        self.plugins = {}
        self.failed_plugins = {}
        self._aliases = {}
        self._descriptors = {descriptor.identifier: descriptor for descriptor in descriptors}
        self._catalog = catalog

        for descriptor in descriptors:
            key = descriptor.identifier
            display_name = descriptor.info.get("name", "")
            display_key = display_name.lower() if isinstance(display_name, str) else ""

            if allowed and key not in allowed and display_key not in allowed:
                logger.debug("Skipping plugin %s because it is not enabled", key)
                continue

            if descriptor.load_error:
                self.failed_plugins[key] = descriptor.load_error
                logger.error("Failed to prepare plugin %s: %s", key, descriptor.load_error)
                continue

            try:
                instance = descriptor.instantiate()
            except Exception as exc:
                message = f"{type(exc).__name__}: {exc}"
                self.failed_plugins[key] = message
                logger.error("Failed to instantiate plugin %s: %s", key, message)
                continue

            self.plugins[key] = instance
            if display_key:
                self._aliases[display_key] = key

        logger.info("Loaded %s plugins (%s failed)", len(self.plugins), len(self.failed_plugins))
        self.initialized = True
        return bool(self.plugins)
    
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
        plugin = self.plugins.get(name)
        if plugin:
            return plugin
        alias = self._aliases.get(name.lower())
        if alias:
            return self.plugins.get(alias)
        return None

    def get_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Expose the catalogued plugin metadata."""

        return {identifier: descriptor.as_dict() for identifier, descriptor in self._descriptors.items()}

    def get_failed_plugins(self) -> Dict[str, str]:
        """Return plugins that failed to load mapped to their error message."""

        return dict(self.failed_plugins)
    
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
