"""Simplified Wi-Fi mapper plugin."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class WifiMapperPlugin(BasePlugin):
    """Parse Wi-Fi mapping exports produced by tools such as Wigle."""

    def __init__(self) -> None:
        super().__init__(
            name="Wi-Fi Mapper",
            description="Load coordinates from Wi-Fi survey exports",
        )

    def get_configuration_options(self) -> List[dict]:
        return [
            {
                "name": "export_path",
                "display_name": "Wi-Fi export file or directory",
                "type": "path",
                "default": "",
                "required": True,
                "description": (
                    "JSON or CSV export containing latitude/longitude pairs.  "
                    "When a directory is provided every matching file is read."
                ),
            },
            {
                "name": "filter_ssid",
                "display_name": "Filter by SSID",
                "type": "string",
                "default": "",
                "description": "Only return entries whose SSID contains this value.",
            },
        ]

    def is_configured(self) -> tuple[bool, str]:
        path = self.config.get("export_path")
        if not path:
            return False, "No Wi-Fi export configured"
        resolved = Path(path).expanduser()
        if not resolved.exists():
            return False, f"Wi-Fi export path does not exist: {path}"
        return True, "WifiMapperPlugin is configured"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        configured, message = self.is_configured()
        if not configured:
            logger.warning("WifiMapperPlugin not configured: %s", message)
            return []

        base_path = Path(self.config["export_path"]).expanduser()
        ssid_filter = (self.config.get("filter_ssid") or "").lower()

        samples: List[LocationPoint] = []
        for path in self._iter_files(base_path):
            try:
                samples.extend(
                    self._parse_file(path, ssid_filter, date_from, date_to)
                )
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to parse %s: %s", path, exc)
        return samples

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    def _iter_files(self, path: Path) -> Iterator[Path]:
        if path.is_dir():
            yield from path.glob("*.json")
            yield from path.glob("*.csv")
        else:
            yield path

    def _parse_file(
        self,
        path: Path,
        ssid_filter: str,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        if path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            rows = payload if isinstance(payload, list) else payload.get("wifi", [])
        else:
            # Very small dependency free CSV reader
            rows = []
            with path.open("r", encoding="utf-8") as handle:
                header = handle.readline().strip().split(",")
                for line in handle:
                    values = line.strip().split(",")
                    rows.append(dict(zip(header, values)))

        for row in rows:
            point = self._parse_row(row, ssid_filter)
            if not point:
                continue
            if date_from and point.timestamp < date_from:
                continue
            if date_to and point.timestamp > date_to:
                continue
            yield point

    def _parse_row(self, row: object, ssid_filter: str) -> Optional[LocationPoint]:
        if not isinstance(row, dict):
            return None

        ssid = str(row.get("ssid") or row.get("name") or "").strip()
        if ssid_filter and ssid_filter not in ssid.lower():
            return None

        lat = row.get("lat") or row.get("latitude")
        lon = row.get("lon") or row.get("lng") or row.get("longitude")
        if lat is None or lon is None:
            return None

        timestamp = row.get("timestamp") or row.get("last_seen")
        parsed_time = self._parse_timestamp(timestamp)

        return LocationPoint(
            latitude=float(lat),
            longitude=float(lon),
            timestamp=parsed_time or datetime.utcnow(),
            source="Wi-Fi Mapper",
            context=ssid or "Wi-Fi access point",
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


Plugin = WifiMapperPlugin
