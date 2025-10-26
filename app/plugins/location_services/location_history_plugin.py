"""Importable version of the location history plugin.

The original repository stored an auto-generated file that could not be parsed
by Python.  The new implementation favours clarity and predictable behaviour –
it consumes simple JSON or CSV exports created by common services and turns
them into :class:`LocationPoint` instances.
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class LocationHistoryPlugin(BasePlugin):
    """Load location samples from a directory of lightweight exports."""

    def __init__(self) -> None:
        super().__init__(
            name="Location History",
            description="Parse lightweight JSON/CSV location history exports",
        )

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------
    def get_configuration_options(self) -> List[dict]:
        return []

    def is_configured(self) -> tuple[bool, str]:
        if self.has_input_data():
            return True, "LocationHistoryPlugin is configured"

        directory = self.get_data_directory()
        return False, f"Add location history exports to {directory}"

    # ------------------------------------------------------------------
    # Public behaviour
    # ------------------------------------------------------------------
    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        """Read all known location files and return matching samples."""

        configured, message = self.is_configured()
        if not configured:
            logger.warning("LocationHistoryPlugin not configured: %s", message)
            return []

        directory = Path(self.get_data_directory()).expanduser()
        samples: List[LocationPoint] = []
        for path in self._iter_location_files(directory):
            try:
                samples.extend(self._load_file(path, date_from, date_to))
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to load %s: %s", path, exc)

        logger.debug(
            "LocationHistoryPlugin returned %d samples from %s",
            len(samples),
            directory,
        )
        return samples

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _iter_location_files(self, directory: Path) -> Iterator[Path]:
        patterns = ("*.json", "*.csv")
        for pattern in patterns:
            yield from directory.glob(pattern)

    def _load_file(
        self,
        path: Path,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        if path.suffix.lower() == ".json":
            return list(self._load_json(path, date_from, date_to))
        if path.suffix.lower() == ".csv":
            return list(self._load_csv(path, date_from, date_to))
        return []

    def _load_json(
        self,
        path: Path,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterator[LocationPoint]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if isinstance(payload, dict):
            candidates = payload.get("locations") or payload.get("history") or []
        else:
            candidates = payload

        for item in candidates:
            point = self._build_location_point(item)
            if not point:
                continue
            if date_from and point.timestamp < date_from:
                continue
            if date_to and point.timestamp > date_to:
                continue
            yield point

    def _load_csv(
        self,
        path: Path,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterator[LocationPoint]:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                point = self._build_location_point(row)
                if not point:
                    continue
                if date_from and point.timestamp < date_from:
                    continue
                if date_to and point.timestamp > date_to:
                    continue
                yield point

    def _build_location_point(self, data: object) -> Optional[LocationPoint]:
        if not isinstance(data, dict):
            return None

        latitude = data.get("lat") or data.get("latitude")
        longitude = data.get("lon") or data.get("lng") or data.get("longitude")
        timestamp = (
            data.get("timestamp")
            or data.get("time")
            or data.get("date")
            or data.get("created_at")
        )

        if latitude is None or longitude is None or timestamp is None:
            return None

        parsed_time = self._parse_timestamp(timestamp)
        if not parsed_time:
            return None

        context = str(data.get("name") or data.get("context") or "Location")
        return LocationPoint(
            latitude=float(latitude),
            longitude=float(longitude),
            timestamp=parsed_time,
            source="Location History",
            context=context,
        )

    @staticmethod
    def _parse_timestamp(value: object) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(float(value))
            except ValueError:
                return None
        if isinstance(value, str):
            for fmt in (
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None


# Backwards compatibility with legacy imports
Plugin = LocationHistoryPlugin
