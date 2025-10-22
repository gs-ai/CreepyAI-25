"""Utility plugin that initialises CreepyAI's plugin directories."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

from app.plugins.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


class Plugin:
    """Initialise on-disk directories and return a summary."""

    def __init__(self) -> None:
        self.name = "Plugin Initialiser"
        self.description = "Prepare local plugin directories"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        self.config_path = Path.home() / ".creepyai" / "config" / "plugins.json"

    def get_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
        }

    def run(self, legacy_dir: str | None = None) -> Dict[str, object]:
        config = self._load_or_create_config()
        directories = [Path(path).expanduser() for path in config["plugin_directories"]]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        plugin_count = 0
        if directories:
            manager = PluginManager(str(directories[0]))
            manager.load_plugins(force_refresh=True)
            plugin_count = len(manager.plugins)
        return {
            "directories": [str(path) for path in directories],
            "disabled": config.get("disabled_plugins", []),
            "plugin_count": plugin_count,
        }

    # ------------------------------------------------------------------
    def _load_or_create_config(self) -> Dict[str, List[str]]:
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text("utf-8"))
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
                logger.warning("Invalid plugin configuration %s: %s", self.config_path, exc)
        default = {
            "plugin_directories": [
                str(Path.home() / ".creepyai" / "plugins"),
                str(Path(__file__).resolve().parents[2] / "plugins"),
            ],
            "disabled_plugins": [],
        }
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default
