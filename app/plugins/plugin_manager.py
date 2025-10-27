"""Plugin management utilities for CreepyAI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from app.plugins.catalog import PluginCatalog

logger = logging.getLogger("creepyai.plugin_manager")


class PluginManager:
    """Light-weight loader and registry of CreepyAI plugins."""

    def __init__(self, plugin_dir: str | Path | None = None) -> None:
        directory = Path(plugin_dir) if plugin_dir else Path(__file__).resolve().parent
        self.plugin_dir: Path = directory
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Any] = {}
        self.failed_plugins: Dict[str, str] = {}
        self._aliases: Dict[str, str] = {}
        self._catalog = PluginCatalog([self.plugin_dir])

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def initialize(self, *, force_refresh: bool = False) -> Dict[str, Any]:
        """Prepare the internal data structures and optionally reload plugins."""

        self.plugins.clear()
        self.failed_plugins.clear()
        self._aliases.clear()
        if force_refresh:
            self.load_plugins(force_refresh=True)
        return self.plugins

    def load_plugins(self, *, force_refresh: bool = False) -> Dict[str, Any]:
        """Discover and instantiate plugins from the configured directory."""

        self.plugins.clear()
        self.failed_plugins.clear()
        self._aliases.clear()

        descriptors = self._catalog.load(force_refresh=force_refresh)
        for descriptor in descriptors:
            key = descriptor.identifier
            if descriptor.load_error:
                self.failed_plugins[key] = descriptor.load_error
                logger.error("Failed to prepare plugin %s: %s", key, descriptor.load_error)
                continue
            try:
                instance = descriptor.instantiate()
            except Exception as exc:  # pragma: no cover - defensive guard
                message = f"{type(exc).__name__}: {exc}"
                self.failed_plugins[key] = message
                logger.error("Failed to instantiate plugin %s: %s", key, message)
                continue
            info = descriptor.info
            self._register_instance(key, instance, info)
        return self.plugins

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register_plugins(self, plugin_classes: Iterable[type]) -> Dict[str, Any]:
        """Register plugins supplied as classes."""

        for plugin_class in plugin_classes:
            identifier = getattr(plugin_class, "__name__", str(plugin_class))
            try:
                instance = plugin_class()
            except Exception as exc:  # pragma: no cover - defensive guard
                message = f"{type(exc).__name__}: {exc}"
                self.failed_plugins[identifier] = message
                logger.error("Failed to instantiate plugin %s: %s", identifier, message)
                continue
            info = getattr(instance, "get_info", lambda: {"name": identifier})()
            self._register_instance(identifier, instance, info)
        return self.plugins

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def get_failed_plugins(self) -> Dict[str, str]:
        """Return a mapping of plugin identifiers to failure reasons."""

        return dict(self.failed_plugins)

    def get_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Return a structured manifest describing loaded plugins."""

        manifest: Dict[str, Dict[str, Any]] = {}
        for identifier, plugin in self.plugins.items():
            info = getattr(plugin, "get_info", lambda: {"name": identifier})()
            manifest[identifier] = {"info": info}
        return manifest

    def get_plugin(self, name: str) -> Optional[Any]:
        """Retrieve a plugin by identifier or human readable name."""

        candidate = self.plugins.get(name)
        if candidate:
            return candidate
        alias = self._aliases.get(name.lower())
        if alias:
            return self.plugins.get(alias)
        return None

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    def execute_plugin(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a plugin by its identifier or alias."""

        plugin = self.get_plugin(name)
        if not plugin:
            logger.error("Plugin %s not found", name)
            return None
        callable_attr = getattr(plugin, "run", None) or getattr(plugin, "execute", None)
        if not callable(callable_attr):
            logger.error("Plugin %s has no executable interface", name)
            return None
        try:
            return callable_attr(*args, **kwargs)
        except Exception as exc:
            logger.exception("Error executing plugin %s: %s", name, exc)
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _register_instance(self, identifier: str, instance: Any, info: Dict[str, Any]) -> None:
        """Add a plugin instance to the registry and record its alias."""

        self.plugins[identifier] = instance
        display_name = info.get("name") if isinstance(info, dict) else None
        if isinstance(display_name, str):
            self._aliases[display_name.lower()] = identifier
