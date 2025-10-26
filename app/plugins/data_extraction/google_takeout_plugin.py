"""Google Takeout data extraction plugin."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class GoogleTakeoutPlugin(BasePlugin):
    """Parse a subset of Google Takeout archives for location information."""

    def __init__(self) -> None:
        super().__init__(
            name="Google Takeout",
            description="Extract location data from Google Takeout exports",
        )

    def get_configuration_options(self) -> List[dict]:
        return []

    def is_configured(self) -> tuple[bool, str]:
        directory = self.config.get("archive_directory")
        if directory and Path(directory).expanduser().exists():
            return True, "GoogleTakeoutPlugin is configured"

        if self.has_input_data():
            return True, "GoogleTakeoutPlugin is configured"

        managed_dir = self.get_data_directory()
        return False, f"Add Google Takeout exports to {managed_dir}"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        directory_setting = self.config.get("archive_directory")
        if directory_setting and Path(directory_setting).expanduser().exists():
            directory = Path(directory_setting).expanduser()
        else:
            if not self.has_input_data():
                logger.warning("GoogleTakeoutPlugin has no data to process")
                return []
            directory = Path(self.get_data_directory()).expanduser()

        samples: List[LocationPoint] = []
        for path in self._iter_json_files(directory):
            try:
                samples.extend(self._parse_file(path, date_from, date_to))
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to parse %s: %s", path, exc)
        return samples

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    def _iter_json_files(self, directory: Path) -> Iterator[Path]:
        for path in directory.rglob("*.json"):
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
            for key in ("locations", "timelineObjects", "items"):
                if key in payload and isinstance(payload[key], list):
                    entries = payload[key]
                    break
            else:
                entries = []
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

        if "latitudeE7" in entry or "longitudeE7" in entry:
            lat = entry.get("latitudeE7")
            lon = entry.get("longitudeE7")
            if isinstance(lat, (int, float)):
                lat = float(lat) / 1e7 if abs(lat) > 90 else float(lat)
            if isinstance(lon, (int, float)):
                lon = float(lon) / 1e7 if abs(lon) > 180 else float(lon)
        else:
            location = entry.get("location") or entry.get("place") or {}
            lat = location.get("latitude") or location.get("lat")
            lon = location.get("longitude") or location.get("lng")

        if lat is None or lon is None:
            return None

        timestamp = (
            entry.get("timestamp")
            or entry.get("timestampMs")
            or entry.get("time")
            or entry.get("date")
        )
        parsed_time = self._parse_timestamp(timestamp)
        if not parsed_time:
            return None

        context = (
            entry.get("title")
            or entry.get("description")
            or entry.get("placeId")
            or "Google Takeout"
        )

        return LocationPoint(
            latitude=float(lat),
            longitude=float(lon),
            timestamp=parsed_time,
            source="Google Takeout",
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


Plugin = GoogleTakeoutPlugin
