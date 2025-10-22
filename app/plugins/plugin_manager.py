"""High-level convenience wrapper around :mod:`app.plugins.catalog`."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from app.plugins.catalog import PluginCatalog


logger = logging.getLogger(__name__)


class PluginManager:
    """Light-weight plugin loader for scripts and tests."""

    def __init__(self, plugin_dir: str):
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Any] = {}
        self.failed_plugins: Dict[str, str] = {}
        self._aliases: Dict[str, str] = {}
        self._catalog = PluginCatalog([self.plugin_dir])

    def load_plugins(self, *, force_refresh: bool = False) -> Dict[str, Any]:
        """Load all plugins from the configured directory."""

        self.plugins = {}
        self.failed_plugins = {}
        self._aliases = {}

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

            self.plugins[key] = instance
            display_name = descriptor.info.get("name")
            if isinstance(display_name, str):
                self._aliases[display_name.lower()] = key

        return self.plugins

    def get_plugin(self, name: str) -> Optional[Any]:
        """Retrieve a plugin by identifier or human readable name."""

        candidate = self.plugins.get(name)
        if candidate:
            return candidate

        alias = self._aliases.get(name.lower())
        if alias:
            return self.plugins.get(alias)
        return None

    def execute_plugin(self, name: str, *args, **kwargs) -> Any:
        """Execute a plugin by name."""

        plugin = self.get_plugin(name)
        if not plugin:
            logger.error("Plugin %s not found", name)
            return None
        return plugin.run(*args, **kwargs)
