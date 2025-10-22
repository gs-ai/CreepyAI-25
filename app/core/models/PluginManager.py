"""Model layer plugin manager built on the shared catalog infrastructure."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.plugins.catalog import PluginCatalog, PluginDescriptor


logger = logging.getLogger(__name__)


class PluginManager:
    """Unified plugin manager for CreepyAI models and view layers."""

    _instance: Optional["PluginManager"] = None

    @classmethod
    def get_instance(cls) -> "PluginManager":
        if cls._instance is None:
            cls._instance = PluginManager()
        return cls._instance

    def __init__(self) -> None:
        if PluginManager._instance is not None:
            return

        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_paths: List[str] = []
        self.loaded = False
        self.failed_plugins: Dict[str, str] = {}
        self._plugin_cache: Dict[str, Any] = {}
        self._catalog: Optional[PluginCatalog] = None
        self._descriptors: Dict[str, PluginDescriptor] = {}

    def set_plugin_paths(self, paths: List[str]) -> None:
        self.plugin_paths = paths
        self.loaded = False
        self._plugin_cache.clear()

    def _default_paths(self) -> List[str]:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../plugins"))
        return [base]

    @lru_cache(maxsize=32)
    def discover_plugins(self, *, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        if self.loaded and not force_refresh:
            return self.plugins

        candidate_paths = self.plugin_paths or self._default_paths()
        prepared_paths: List[str] = []
        for path in candidate_paths:
            try:
                os.makedirs(path, exist_ok=True)
                prepared_paths.append(path)
            except Exception as exc:
                logger.error("Unable to prepare plugin path %s: %s", path, exc)

        if not prepared_paths:
            logger.warning("No plugin directories available for discovery")
            self.plugins = {}
            self.failed_plugins = {}
            self.loaded = True
            return self.plugins

        try:
            catalog = PluginCatalog(prepared_paths)
        except ValueError as exc:
            logger.error("Failed to create plugin catalog: %s", exc)
            self.plugins = {}
            self.failed_plugins = {}
            self.loaded = True
            return self.plugins

        descriptors = catalog.load(force_refresh=force_refresh)
        self._catalog = catalog
        self._descriptors = {descriptor.identifier: descriptor for descriptor in descriptors}
        self.plugins = {}
        self.failed_plugins = {}

        for descriptor in descriptors:
            key = descriptor.identifier
            info = descriptor.info.copy()
            display_name = info.get("name") or key
            info.setdefault("description", "")
            info.setdefault("version", "0.0")
            info.setdefault("author", "Unknown")

            if descriptor.load_error:
                self.failed_plugins[key] = descriptor.load_error
                logger.error("Plugin %s failed catalog validation: %s", key, descriptor.load_error)
                continue

            try:
                instance = descriptor.instantiate()
            except Exception as exc:
                message = f"{type(exc).__name__}: {exc}"
                self.failed_plugins[key] = message
                logger.error("Plugin %s could not be instantiated: %s", key, message)
                continue

            self.plugins[display_name] = {
                "name": display_name,
                "identifier": key,
                "path": descriptor.path,
                "instance": instance,
                "module": descriptor.module,
                "description": info.get("description", ""),
                "version": info.get("version", "0.0"),
                "author": info.get("author", "Unknown"),
                "metadata": info,
            }

            logger.info("Loaded plugin: %s v%s", display_name, info.get("version", "0.0"))

        self.loaded = True
        self._plugin_cache.clear()
        return self.plugins

    def get_plugin(self, name: str) -> Optional[Any]:
        if not self.loaded:
            self.discover_plugins()

        if name in self._plugin_cache:
            return self._plugin_cache[name]

        plugin_data = self.plugins.get(name)
        if plugin_data:
            self._plugin_cache[name] = plugin_data["instance"]
            return plugin_data["instance"]
        return None

    def get_plugin_names(self) -> List[str]:
        if not self.loaded:
            self.discover_plugins()
        return list(self.plugins.keys())

    def run_plugin(self, name: str, method: str, *args, **kwargs) -> Any:
        plugin = self.get_plugin(name)
        if not plugin:
            logger.error("Plugin not found: %s", name)
            return None

        if not hasattr(plugin, method):
            logger.error("Method not found in plugin %s: %s", name, method)
            return None

        try:
            return getattr(plugin, method)(*args, **kwargs)
        except Exception as exc:
            logger.error("Error running plugin %s.%s: %s", name, method, exc)
            logger.debug("Exception details:", exc_info=True)
            return None

    def get_input_plugins(self) -> List[Any]:
        plugins = self.discover_plugins()
        return [data["instance"] for data in plugins.values() if hasattr(data["instance"], "returnLocations")]

    def get_manifest(self) -> Dict[str, Dict[str, Any]]:
        return {identifier: descriptor.as_dict() for identifier, descriptor in self._descriptors.items()}

    def get_failed_plugins(self) -> Dict[str, str]:
        return dict(self.failed_plugins)
