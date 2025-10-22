"""
CreepyAI Plugin System
"""
import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.plugins.catalog import PluginCatalog, PluginDescriptor

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages loading and running of CreepyAI plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugin_dirs: List[str] = []
        self.categories: Dict[str, str] = {}
        self.failed_plugins: Dict[str, str] = {}
        self._descriptors: Dict[str, PluginDescriptor] = {}
        self._catalog_cache_path: Optional[Path] = None
        
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
    
    def discover_plugins(self, *, force_refresh: bool = False):
        """Discover all available plugins in the plugin directories."""

        self.plugins = {}
        self.categories = {}
        self.failed_plugins = {}

        catalog = PluginCatalog(self.plugin_dirs, cache_path=self._ensure_catalog_cache_path())
        descriptors = catalog.load(force_refresh=force_refresh)
        self._descriptors = {descriptor.identifier: descriptor for descriptor in descriptors}

        for descriptor in descriptors:
            if descriptor.load_error:
                self.failed_plugins[descriptor.identifier] = descriptor.load_error
                continue

            try:
                plugin_instance = descriptor.instantiate()
                self._ensure_required_methods(plugin_instance)
                self.plugins[descriptor.identifier] = plugin_instance
                self.categories[descriptor.identifier] = descriptor.category
            except Exception as exc:  # pragma: no cover - safe guard
                message = f"{type(exc).__name__}: {exc}"
                self.failed_plugins[descriptor.identifier] = message

        logger.info(
            "Discovered %s plugins (%s failed) across %s categories",
            len(self.plugins),
            len(self.failed_plugins),
            len(set(self.categories.values())),
        )
        return self.plugins

    def _ensure_catalog_cache_path(self) -> Path:
        if self._catalog_cache_path is None:
            cache_dir = Path.home() / ".creepyai" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self._catalog_cache_path = cache_dir / "plugin_catalog.json"
        return self._catalog_cache_path
    
    def _scan_directory(self, directory, category='uncategorized'):
        """Deprecated in favour of the catalog based discovery."""
        logger.debug(
            "PluginManager._scan_directory is deprecated; catalog performs discovery for %s",
            directory,
        )
        return None
    
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

    def describe_plugin(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Return the descriptor metadata for a specific plugin."""

        descriptor = self._descriptors.get(identifier)
        if descriptor is None:
            return None
        payload = descriptor.as_dict().copy()
        if identifier in self.failed_plugins:
            payload["load_error"] = self.failed_plugins[identifier]
        return payload

    def get_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Expose the complete plugin manifest for telemetry and tooling."""

        return {identifier: descriptor.as_dict() for identifier, descriptor in self._descriptors.items()}

    def get_failed_plugins(self) -> Dict[str, str]:
        """Return a mapping of plugin identifiers to the reason they failed to load."""

        return dict(self.failed_plugins)
    
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
