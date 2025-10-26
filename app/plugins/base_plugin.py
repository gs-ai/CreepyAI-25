#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Base plugin class and data structures for CreepyAI
"""

import os
import json
import logging
import re
import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib
from dataclasses import dataclass

from app.core.path_utils import get_user_data_dir, get_app_root

logger = logging.getLogger(__name__)

@dataclass
class LocationPoint:
    """Represents a geographic point with metadata"""
    latitude: float
    longitude: float
    timestamp: datetime
    source: str
    context: str

class BasePlugin:
    """Base class for all CreepyAI plugins"""
    
    def __init__(self, name: str, description: str, *, data_directory_name: Optional[str] = None):
        self.name = name
        self.description = description
        self._import_root = Path(get_user_data_dir()) / "imports"
        self._import_root.mkdir(parents=True, exist_ok=True)

        directory_name = self._normalise_directory_name(data_directory_name or self.name)

        self._default_input_dir = self._import_root / directory_name
        self._default_input_dir.mkdir(parents=True, exist_ok=True)

        self.data_dir = os.path.join(
            os.path.expanduser("~"),
            ".creepyai",
            "data",
            self.__class__.__name__
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self.config: Dict[str, Any] = {
            "data_directory": str(self._default_input_dir)
        }
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """
        Return configuration options for this plugin
        
        Returns:
            List of dictionaries with the following keys:
            - name: Configuration option name
            - display_name: Display name for the UI
            - type: Type of configuration (string, boolean, directory, file, etc.)
            - default: Default value
            - required: Whether the option is required
            - description: Description of the option
        """
        return []
    
    def is_configured(self) -> Tuple[bool, str]:
        """
        Check if the plugin is properly configured
        
        Returns:
            Tuple of (is_configured, message)
        """
        return True, f"{self.name} is configured"
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Update the configuration for this plugin
        
        Args:
            config: Dictionary of configuration options
            
        Returns:
            True if successful, False otherwise
        """
        if not isinstance(config, dict):
            return False

        # Preserve the managed data directory when callers omit it
        if "data_directory" not in config and "data_directory" not in self.config:
            self.config["data_directory"] = str(self._default_input_dir)

        self.config.update(config)

        if not self.config.get("data_directory"):
            self.config["data_directory"] = str(self._default_input_dir)

        return True

    def get_data_directory(self) -> str:
        """Return the user-managed data directory for this plugin."""
        # New logic: prefer a repository-local INPUT-DATA directory so users can
        # drop datasets inside the project workspace. This avoids placing data
        # deep inside the user's Application Support folders.
        try:
            repo_root = get_app_root()
            repo_input = repo_root / "INPUT-DATA"
            # Ensure the repo-local input root exists
            repo_input.mkdir(parents=True, exist_ok=True)

            # Prefer a plugin-named subdirectory inside INPUT-DATA (e.g. INPUT-DATA/www.yelp.com)
            candidate = repo_input / self._default_input_dir.name
            candidate.mkdir(parents=True, exist_ok=True)
            return str(candidate)
        except Exception:
            # If anything goes wrong creating the repo-local input dir, fall back
            # to the configured data_directory or the per-user default under imports
            configured = self.config.get("data_directory")
            if not configured:
                configured = str(self._default_input_dir)

            path = Path(str(configured)).expanduser()
            if not path.is_absolute():
                path = self._import_root / path

            # If the path is intended to be a ZIP file ensure the parent exists, otherwise
            # create the directory so the user has a predictable drop location.
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
                candidate for candidate in data_path.glob("*.zip")
                if zipfile.is_zipfile(candidate)
            )
            if zip_candidates:
                return self._extract_zipfile(zip_candidates[0], temp_folder)
            return str(data_path)

        return str(data_path)

    def has_input_data(self) -> bool:
        """Return True when the managed input directory contains user-provided data."""

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

    def _slugify_name(self, value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_")
        if not slug:
            slug = self.__class__.__name__.lower()
        return slug.lower()

    def _normalise_directory_name(self, value: str) -> str:
        if not value:
            return self._slugify_name(self.name)

        value = value.strip()
        if not value:
            return self._slugify_name(self.name)

        # Prevent path traversal while preserving descriptive names (including dots)
        value = value.replace("\\", "_").replace("/", "_")

        # Avoid names consisting solely of dots after sanitisation
        cleaned = value.strip(".")
        if not cleaned:
            return self._slugify_name(self.name)

        return value

    def _extract_zipfile(self, zip_path: Path, temp_folder: str) -> str:
        target_dir = Path(self.data_dir) / temp_folder
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)

        return str(target_dir)
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                          date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Collect location data for the specified target
        
        Args:
            target: Target to collect locations for (e.g., username, path)
            date_from: Filter results to those after this date
            date_to: Filter results to those before this date
            
        Returns:
            List of LocationPoint objects
        """
        return []
    
    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for potential targets matching the search term
        
        Args:
            search_term: Search term
            
        Returns:
            List of dictionaries with the following keys:
            - targetId: Unique identifier for the target
            - targetName: Display name for the target
            - pluginName: Name of the plugin that found the target
        """
        return []
