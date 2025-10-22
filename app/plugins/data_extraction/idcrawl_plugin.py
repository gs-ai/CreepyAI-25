"""Simplified IDCrawl integration plugin."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class IDCrawlPlugin(BasePlugin):
    """Load cached IDCrawl results and expose them to the application."""

    def __init__(self) -> None:
        super().__init__(
            name="IDCrawl",
            description="Read cached IDCrawl search results",
        )

    def get_configuration_options(self) -> List[dict]:
        return [
            {
                "name": "results_file",
                "display_name": "IDCrawl JSON file",
                "type": "file",
                "default": "",
                "required": True,
                "description": (
                    "Path to a JSON file produced by IDCrawl.  The file must "
                    "contain a list of entries with latitude/longitude "
                    "information."
                ),
            }
        ]

    def is_configured(self) -> tuple[bool, str]:
        path = self.config.get("results_file")
        if not path:
            return False, "No IDCrawl results file configured"
        resolved = Path(path).expanduser()
        if not resolved.exists():
            return False, f"IDCrawl results file does not exist: {path}"
        return True, "IDCrawlPlugin is configured"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        configured, message = self.is_configured()
        if not configured:
            logger.warning("IDCrawlPlugin not configured: %s", message)
            return []

        path = Path(self.config["results_file"]).expanduser()
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # pragma: no cover - fallback path
            logger.error("Failed to load %s: %s", path, exc)
            return []

        entries = payload if isinstance(payload, list) else payload.get("results", [])
        points: List[LocationPoint] = []
        for entry in entries:
            point = self._parse_entry(entry)
            if not point:
                continue
            if date_from and point.timestamp < date_from:
                continue
            if date_to and point.timestamp > date_to:
                continue
            points.append(point)
        return points

    def run(self, target: str | None = None) -> List[LocationPoint]:
        return self.collect_locations(target)

    @staticmethod
    def _parse_entry(entry: object) -> Optional[LocationPoint]:
        if not isinstance(entry, dict):
            return None

        lat = entry.get("latitude") or entry.get("lat")
        lon = entry.get("longitude") or entry.get("lon")
        if lat is None or lon is None:
            return None

        timestamp_value = entry.get("timestamp") or entry.get("date")
        parsed_time = IDCrawlPlugin._parse_timestamp(timestamp_value)

        context = entry.get("name") or entry.get("label") or "IDCrawl"
        return LocationPoint(
            latitude=float(lat),
            longitude=float(lon),
            timestamp=parsed_time or datetime.utcnow(),
            source="IDCrawl",
            context=str(context),
        )

    @staticmethod
    def _parse_timestamp(value: object) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(float(value))
            except ValueError:
                return None
        if isinstance(value, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None


Plugin = IDCrawlPlugin
