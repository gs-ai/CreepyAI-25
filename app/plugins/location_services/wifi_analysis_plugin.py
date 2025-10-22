"""Wi-Fi analysis helper plugin."""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class WifiAnalysisPlugin(BasePlugin):
    """Provide lightweight analytics for Wi-Fi survey exports."""

    def __init__(self) -> None:
        super().__init__(
            name="Wi-Fi Analysis",
            description="Summarise Wi-Fi survey data and highlight hotspots",
        )
        self._summary: Dict[str, object] = {}

    def get_configuration_options(self) -> List[dict]:
        return [
            {
                "name": "export_path",
                "display_name": "Wi-Fi export path",
                "type": "path",
                "default": "",
                "required": True,
                "description": "JSON export produced by the Wi-Fi mapper plugin.",
            }
        ]

    def is_configured(self) -> tuple[bool, str]:
        path = self.config.get("export_path")
        if not path:
            return False, "No export path configured"
        resolved = Path(path).expanduser()
        if not resolved.exists():
            return False, f"Wi-Fi export path does not exist: {path}"
        return True, "WifiAnalysisPlugin is configured"

    def collect_locations(
        self,
        target: str | None = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        configured, message = self.is_configured()
        if not configured:
            logger.warning("WifiAnalysisPlugin not configured: %s", message)
            return []

        path = Path(self.config["export_path"]).expanduser()
        points = list(self._load_points(path, date_from, date_to))
        self._summary = self._build_summary(points)
        return points

    def run(self, target: str | None = None) -> Dict[str, object]:
        self.collect_locations(target)
        return self._summary

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _load_points(
        self,
        path: Path,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[LocationPoint]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        rows = payload if isinstance(payload, list) else payload.get("wifi", [])

        for row in rows:
            point = self._parse_row(row)
            if not point:
                continue
            if date_from and point.timestamp < date_from:
                continue
            if date_to and point.timestamp > date_to:
                continue
            yield point

    @staticmethod
    def _parse_row(row: object) -> Optional[LocationPoint]:
        if not isinstance(row, dict):
            return None
        lat = row.get("lat") or row.get("latitude")
        lon = row.get("lon") or row.get("lng") or row.get("longitude")
        if lat is None or lon is None:
            return None
        timestamp = row.get("timestamp")
        try:
            parsed_time = datetime.fromtimestamp(float(timestamp)) if timestamp else datetime.utcnow()
        except (TypeError, ValueError):
            parsed_time = datetime.utcnow()
        context = row.get("ssid") or row.get("name") or "Wi-Fi network"
        return LocationPoint(
            latitude=float(lat),
            longitude=float(lon),
            timestamp=parsed_time,
            source="Wi-Fi Analysis",
            context=str(context),
        )

    @staticmethod
    def _build_summary(points: List[LocationPoint]) -> Dict[str, object]:
        if not points:
            return {"total_points": 0, "top_ssids": [], "bounding_box": None}

        ssids = Counter(point.context for point in points)
        top_ssids = ssids.most_common(5)

        latitudes = [p.latitude for p in points]
        longitudes = [p.longitude for p in points]
        bounding_box = {
            "north": max(latitudes),
            "south": min(latitudes),
            "east": max(longitudes),
            "west": min(longitudes),
        }

        return {
            "total_points": len(points),
            "top_ssids": top_ssids,
            "bounding_box": bounding_box,
        }


Plugin = WifiAnalysisPlugin
