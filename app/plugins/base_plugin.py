"""Base class and data structures for CreepyAI plugins.

This module defines the abstract base class ``BasePlugin`` that all
plugins should inherit from. It provides functionality for managing
plugin-specific data directories, configuration, and defines stubs for
location collection and target search that concrete plugins must
implement. The ``LocationPoint`` dataclass encapsulates geographic
coordinates with metadata.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Iterable

from app.core.path_utils import get_user_data_dir, get_app_root


logger = logging.getLogger("creepyai.base_plugin")


@dataclass
class LocationPoint:
    """Represents a geographic point with metadata."""
    latitude: float
    longitude: float
    timestamp: datetime
    source: str
    context: str


class BasePlugin:
    """Base class for all CreepyAI plugins.

    Concrete plugins should subclass ``BasePlugin`` and override
    ``collect_locations`` and ``search_for_targets``. The base class
    manages user-supplied data directories and provides configuration
    handling helpers.
    """

    def __init__(self, name: str, description: str, *, data_directory_name: Optional[str] = None) -> None:
        self.name: str = name
        self.description: str = description
        # Root directory for imported data
        self._import_root: Path = Path(get_user_data_dir()) / "imports"
        self._import_root.mkdir(parents=True, exist_ok=True)

        directory_name: str = self._normalise_directory_name(data_directory_name or self.name)
        self._default_input_dir: Path = self._import_root / directory_name
        self._default_input_dir.mkdir(parents=True, exist_ok=True)

        # Per-plugin data directory under the user’s home
        self.data_dir: Path = Path.home() / ".creepyai" / "data" / self.__class__.__name__
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config: Dict[str, Any] = {"data_directory": str(self._default_input_dir)}

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Return configuration options for this plugin.

        Plugins may override this method to expose configuration options
        in the GUI. Each item in the returned list should be a mapping
        with at least the keys ``name``, ``display_name``, ``type`` and
        ``description``.
        """
        return []

    def is_configured(self) -> Tuple[bool, str]:
        """Check whether the plugin is properly configured.

        Returns
        -------
        tuple
            A tuple ``(configured, message)`` indicating whether the
            plugin is ready for use and a descriptive message.
        """
        return True, f"{self.name} is configured"

    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update the configuration for this plugin.

        This method merges the provided configuration with any existing
        values. If the ``data_directory`` key is omitted the current
        value is preserved.
        """
        if not isinstance(config, dict):
            return False

        if "data_directory" not in config and "data_directory" not in self.config:
            self.config["data_directory"] = str(self._default_input_dir)

        self.config.update(config)
        if not self.config.get("data_directory"):
            self.config["data_directory"] = str(self._default_input_dir)
        return True

    # ------------------------------------------------------------------
    # Data directory helpers
    # ------------------------------------------------------------------
    def get_data_directory(self) -> str:
        """Return the managed data directory for this plugin.

        The method attempts to create a directory under a repository-local
        ``INPUT-DATA`` folder. If that fails it falls back to the
        configured ``data_directory`` or the default input directory.
        """
        try:
            repo_root = Path(get_app_root())
            repo_input = repo_root / "INPUT-DATA"
            repo_input.mkdir(parents=True, exist_ok=True)
            candidate = repo_input / self._default_input_dir.name
            candidate.mkdir(parents=True, exist_ok=True)
            return str(candidate)
        except Exception:
            configured = self.config.get("data_directory", str(self._default_input_dir))
            path = Path(configured).expanduser()
            if not path.is_absolute():
                path = self._import_root / path
            # Ensure the parent of a zip archive exists
            if path.suffix.lower() == ".zip":
                path.parent.mkdir(parents=True, exist_ok=True)
                return str(path)
            path.mkdir(parents=True, exist_ok=True)
            return str(path)

    def prepare_data_directory(self, temp_folder: str) -> str:
        """Return a directory ready for processing, extracting ZIP archives if needed."""
        data_path = Path(self.get_data_directory())
        if data_path.is_file() and data_path.suffix.lower() == ".zip":
            return self._extract_zipfile(data_path, temp_folder)
        if data_path.is_dir():
            zip_candidates = sorted(
                candidate for candidate in data_path.glob("*.zip") if zipfile.is_zipfile(candidate)
            )
            if zip_candidates:
                return self._extract_zipfile(zip_candidates[0], temp_folder)
            return str(data_path)
        return str(data_path)

    def has_input_data(self) -> bool:
        """Return ``True`` if the managed input directory contains data."""
        data_path = Path(self.get_data_directory())
        if data_path.is_file():
            return data_path.exists()
        if data_path.is_dir():
            try:
                next(data_path.iterdir())
            except StopIteration:
                return False
            else:
                return True
        return False

    # ------------------------------------------------------------------
    # Public API to be overridden
    # ------------------------------------------------------------------
    def collect_locations(
        self, target: str, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None
    ) -> List[LocationPoint]:
        """Collect location data for the specified target.

        Concrete plugins must override this method to implement their data
        collection logic. The default implementation returns an empty
        list.
        """
        return []

    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for potential targets matching the search term.

        Concrete plugins must override this method to implement their
        search logic. The default implementation returns an empty list.
        """
        return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _slugify_name(self, value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_")
        return slug.lower() or self.__class__.__name__.lower()

    def _normalise_directory_name(self, value: str) -> str:
        if not value:
            return self._slugify_name(self.name)
        value = value.strip()
        if not value:
            return self._slugify_name(self.name)
        value = value.replace("\\", "_").replace("/", "_")
        cleaned = value.strip(".")
        if not cleaned:
            return self._slugify_name(self.name)
        return value

    def _extract_zipfile(self, zip_path: Path, temp_folder: str) -> str:
        target_dir = self.data_dir / temp_folder
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)
        return str(target_dir)