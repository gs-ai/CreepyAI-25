"""Google Maps export parser used by CreepyAI."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class GoogleMapsPlugin(BasePlugin):
    """Parse the simplified Google Maps takeout format."""

    def __init__(self) -> None:
        super().__init__(
            name="Google Maps",
            description="Read Google Maps location history exports",
        )

    def get_configuration_options(self) -> List[dict]:
        return [
            {
                "name": "takeout_path",
                "display_name": "Google Takeout file or directory",
                "type": "path",
                "default": "",
                "required": True,
                "description": (
                    "Path to a JSON file exported from Google Maps Timeline.  "
                    "You can also point to a directory that contains multiple "
                    "files and the plugin will load each of them."
                ),
            }
        ]

    def is_configured(self) -> tuple[bool, str]:
        path = self.config.get("takeout_path")
        if not path:
            return False, "No takeout export configured"
        resolved = Path(path).expanduser()
        if not resolved.exists():
            return False, f"Takeout path does not exist: {path}"
        return True, "GoogleMapsPlugin is configured"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        configured, message = self.is_configured()
        if not configured:
            logger.warning("GoogleMapsPlugin not configured: %s", message)
            return []

        base_path = Path(self.config["takeout_path"]).expanduser()
        points: List[LocationPoint] = []
        for path in self._iter_files(base_path):
            try:
                points.extend(self._parse_file(path, date_from, date_to))
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to parse %s: %s", path, exc)
        return points

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    def _iter_files(self, path: Path) -> Iterator[Path]:
        if path.is_dir():
            yield from path.glob("*.json")
        else:
            yield path

    def _parse_file(
        self,
        path: Path,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict):
            entries = payload.get("locations") or payload.get("timelineObjects") or []
        else:
            entries = payload

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

        if "location" in entry:
            entry = entry["location"]

        latitude = entry.get("latitudeE7") or entry.get("latitude")
        longitude = entry.get("longitudeE7") or entry.get("longitude")
        if latitude is None or longitude is None:
            return None

        if isinstance(latitude, (int, float)) and abs(latitude) > 90:
            latitude = float(latitude) / 1e7
        if isinstance(longitude, (int, float)) and abs(longitude) > 180:
            longitude = float(longitude) / 1e7

        timestamp = (
            entry.get("timestamp")
            or entry.get("timestampMs")
            or entry.get("time")
            or entry.get("createTimestampMs")
        )

        parsed_time = self._parse_timestamp(timestamp)
        if not parsed_time:
            return None

        context = entry.get("placeId") or entry.get("name") or "Google Maps"
        return LocationPoint(
            latitude=float(latitude),
            longitude=float(longitude),
            timestamp=parsed_time,
            source="Google Maps",
            context=str(context),
        )

    @staticmethod
    def _parse_timestamp(value: object) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
            try:
                return datetime.fromtimestamp(int(value) / 1000)
            except (ValueError, TypeError):
                return None
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(float(value) / (1000 if value > 10**12 else 1))
            except ValueError:
                return None
        return None


Plugin = GoogleMapsPlugin
