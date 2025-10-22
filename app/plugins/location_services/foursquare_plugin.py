"""Foursquare check-in parser."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class FoursquarePlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__(
            name="Foursquare",
            description="Parse Foursquare/Swarm check-in exports",
        )

    def get_configuration_options(self) -> List[dict]:
        return [
            {
                "name": "export_directory",
                "display_name": "Export directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": (
                    "Directory containing check-in JSON files downloaded from "
                    "Foursquare or Swarm."
                ),
            }
        ]

    def is_configured(self) -> tuple[bool, str]:
        directory = self.config.get("export_directory")
        if not directory:
            return False, "No export directory configured"
        resolved = Path(directory).expanduser()
        if not resolved.exists():
            return False, f"Export directory does not exist: {directory}"
        return True, "FoursquarePlugin is configured"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        configured, message = self.is_configured()
        if not configured:
            logger.warning("FoursquarePlugin not configured: %s", message)
            return []

        directory = Path(self.config["export_directory"]).expanduser()
        points: List[LocationPoint] = []
        for path in self._iter_files(directory):
            try:
                points.extend(self._parse_file(path, date_from, date_to))
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to parse %s: %s", path, exc)
        return points

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    def _iter_files(self, directory: Path) -> Iterator[Path]:
        yield from directory.glob("*.json")

    def _parse_file(
        self,
        path: Path,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        entries = payload.get("checkins") if isinstance(payload, dict) else payload
        for entry in entries:
            point = self._parse_entry(entry)
            if not point:
                continue
            if date_from and point.timestamp < date_from:
                continue
            if date_to and point.timestamp > date_to:
                continue
            yield point

    def _parse_entry(self, entry: object) -> Optional[LocationPoint]:
        if not isinstance(entry, dict):
            return None

        venue = entry.get("venue", {})
        location = venue.get("location", {})
        lat = location.get("lat") or location.get("latitude")
        lon = location.get("lng") or location.get("longitude")
        if lat is None or lon is None:
            return None

        timestamp = entry.get("createdAt") or entry.get("timestamp")
        parsed_time = self._parse_timestamp(timestamp)
        if not parsed_time:
            return None

        context = venue.get("name") or entry.get("type") or "Foursquare check-in"
        return LocationPoint(
            latitude=float(lat),
            longitude=float(lon),
            timestamp=parsed_time,
            source="Foursquare",
            context=str(context),
        )

    @staticmethod
    def _parse_timestamp(value: object) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(float(value))
            return datetime.fromisoformat(str(value))
        except ValueError:
            return None


Plugin = FoursquarePlugin
