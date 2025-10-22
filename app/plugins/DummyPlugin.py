"""Dummy plugin used by the automated test-suite."""

from __future__ import annotations

import configparser
import logging
import math
import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.plugins.plugin_base import LocationPoint, PluginBase

logger = logging.getLogger("creepyai.plugins.dummy")


class DummyPlugin(PluginBase):
    """A minimal plugin that simulates returning location data."""

    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self.name = "DummyPlugin"
        self.description = "A simple plugin for testing"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"

        self.settings: Dict[str, Any] = {}
        if settings:
            self.settings.update(settings)

        self._load_config_from_conf()

    # ------------------------------------------------------------------
    # Configuration helpers
    def _load_config_from_conf(self) -> None:
        """Load configuration overrides from ``DummyPlugin.conf`` if present."""

        config_path = os.path.join(os.path.dirname(__file__), "DummyPlugin.conf")
        if not os.path.exists(config_path):
            return

        parser = configparser.ConfigParser()
        parser.read(config_path)
        for section in parser.sections():
            for key, value in parser.items(section):
                self.settings[key] = value

    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Describe configuration values understood by the plugin."""

        return [
            {
                "name": "base_latitude",
                "display_name": "Base Latitude",
                "type": "float",
                "default": 37.7749,
                "required": True,
                "description": "Base latitude for generating locations",
            },
            {
                "name": "base_longitude",
                "display_name": "Base Longitude",
                "type": "float",
                "default": -122.4194,
                "required": True,
                "description": "Base longitude for generating locations",
            },
            {
                "name": "location_variance",
                "display_name": "Location Variance (meters)",
                "type": "int",
                "default": 100,
                "required": True,
                "description": "Variance in meters for generating random locations",
            },
            {
                "name": "location_count",
                "display_name": "Number of Locations",
                "type": "int",
                "default": 10,
                "required": True,
                "description": "Number of locations to generate",
            },
            {
                "name": "date_range_days",
                "display_name": "Date Range (days)",
                "type": "int",
                "default": 30,
                "required": True,
                "description": "Date range in days for generating random timestamps",
            },
        ]

    def is_configured(self) -> Tuple[bool, str]:
        """Return whether the plugin is properly configured."""

        required_keys = {
            option["name"] for option in self.get_configuration_options()
        }
        missing = [key for key in required_keys if key not in self.settings]
        if missing:
            return False, f"Missing required configuration: {', '.join(sorted(missing))}"
        return True, "Dummy plugin is configured"

    # ------------------------------------------------------------------
    # Core functionality
    def collect_locations(
        self,
        target: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        """Generate simulated :class:`LocationPoint` objects."""

        base_lat = float(self.settings.get("base_latitude", 37.7749))
        base_lon = float(self.settings.get("base_longitude", -122.4194))
        variance = int(self.settings.get("location_variance", 100))
        count = int(self.settings.get("location_count", 10))
        date_range_days = int(self.settings.get("date_range_days", 30))

        locations: List[LocationPoint] = []
        for _ in range(count):
            lat_offset = random.uniform(-variance, variance) / 111_320
            lon_offset = random.uniform(-variance, variance) / (
                111_320 * math.cos(math.radians(base_lat))
            )
            timestamp = datetime.now() - timedelta(days=random.randint(0, date_range_days))
            location = LocationPoint(
                latitude=base_lat + lat_offset,
                longitude=base_lon + lon_offset,
                timestamp=timestamp,
                source=self.name,
                context=f"Simulated location for {target}",
            )
            locations.append(location)

        if date_from or date_to:
            locations = [
                loc
                for loc in locations
                if (date_from is None or loc.timestamp >= date_from)
                and (date_to is None or loc.timestamp <= date_to)
            ]

        return locations

    def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        """Execute the plugin and return a success payload."""

        logger.info("DummyPlugin executing with args: %s kwargs: %s", args, kwargs)
        return {"status": "success", "message": "DummyPlugin executed successfully"}

    # ------------------------------------------------------------------
    # Informational helpers
    def get_info(self) -> Dict[str, Any]:
        """Return metadata about the plugin."""

        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
        }

    def get_requirements(self) -> List[str]:
        """Return the plugin's external dependencies."""

        return []

    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""

        logger.debug("Cleaning up %s", self.name)


# Backwards compatibility for code expecting ``Plugin``
Plugin = DummyPlugin

