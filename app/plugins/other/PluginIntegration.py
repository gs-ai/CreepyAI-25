"""Helper plugin that exposes the modern plugin manager to legacy callers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.plugins.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


class Plugin:
    """Provide a very small façade over :class:`PluginManager`."""

    def __init__(self) -> None:
        self.name = "Plugin Integration"
        self.description = "Expose PluginManager to legacy scripts"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        self._manager: Optional[PluginManager] = None

    # Metadata -------------------------------------------------------
    def get_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
        }

    # Behaviour ------------------------------------------------------
    def _ensure_manager(self, plugin_dir: Path) -> PluginManager:
        if self._manager is None or self._manager.plugin_dir != plugin_dir:
            self._manager = PluginManager(str(plugin_dir))
        return self._manager

    def run(self, plugin_directory: str | None = None) -> Dict[str, object]:
        directory = Path(plugin_directory or Path(__file__).resolve().parents[2] / "plugins")
        manager = self._ensure_manager(directory)
        plugins = manager.load_plugins(force_refresh=True)
        manifest = manager.get_manifest() if hasattr(manager, "get_manifest") else {}
        return {
            "plugin_directory": str(directory),
            "plugins": list(plugins.keys()),
            "manifest": manifest,
        }

    # Convenience helpers for legacy code ---------------------------
    def list_plugins(self, plugin_directory: str | None = None) -> List[str]:
        return list(self.run(plugin_directory)["plugins"])

    def get_plugin(self, name: str, plugin_directory: str | None = None):
        directory = Path(plugin_directory or Path(__file__).resolve().parents[2] / "plugins")
        manager = self._ensure_manager(directory)
        manager.load_plugins()
        return manager.get_plugin(name)
