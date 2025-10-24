"""Offline-only GeoIP plugin used by CreepyAI.

This implementation provides deterministic IP to location lookups without
contacting external services.  It consumes a local CSV database describing IP
ranges and their associated coordinates.  A small starter dataset is copied into
``~/.creepyai/data/GeoIPPlugin/`` the first time the plugin runs so users can see
results immediately while remaining fully offline.
"""

from __future__ import annotations

import csv
import ipaddress
import logging
import shutil
from bisect import bisect_right
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Dict, Iterable, List, Optional, Tuple

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class GeoIPPlugin(BasePlugin):
    """Look up approximate coordinates for IP addresses without APIs."""

    _KNOWN_IPS: Dict[str, Tuple[float, float, str]] = {
        "8.8.8.8": (37.3861, -122.0839, "Google Public DNS"),
        "1.1.1.1": (-33.4940, 143.2104, "Cloudflare DNS"),
        "9.9.9.9": (41.5000, -81.6950, "Quad9 DNS"),
        "208.67.222.222": (37.7697, -122.3933, "OpenDNS"),
    }

    def __init__(self) -> None:
        super().__init__(
            name="GeoIP",
            description="Derive approximate coordinates for IP addresses",
        )

        self._default_database_path = Path(self.data_dir) / "geoip_database.csv"
        self.config.setdefault("database_path", str(self._default_database_path))
        self.config.setdefault("fallback_precision", 2)

        self._database_path: Optional[Path] = None
        self._database_mtime: Optional[float] = None
        self._range_starts: List[int] = []
        self._ranges: List[Tuple[int, int, float, float, str]] = []
        self._cache: Dict[str, LocationPoint] = {}
        self._lock = Lock()

        self._ensure_database_exists()

    # ------------------------------------------------------------------
    # Plugin metadata helpers
    # ------------------------------------------------------------------
    def get_configuration_options(self) -> List[Dict[str, object]]:
        return [
            {
                "name": "database_path",
                "display_name": "GeoIP CSV database",
                "type": "file",
                "default": str(self._default_database_path),
                "required": True,
                "description": (
                    "Path to a CSV file with columns ip_start, ip_end, latitude, "
                    "longitude, city, region, country.  A starter dataset is "
                    "created automatically if the file does not exist."
                ),
            },
            {
                "name": "fallback_precision",
                "display_name": "Fallback precision",
                "type": "integer",
                "default": 2,
                "description": (
                    "Number of decimal places to keep when deriving pseudo "
                    "coordinates for unknown IP addresses"
                ),
            },
        ]

    def is_configured(self) -> Tuple[bool, str]:
        try:
            path = self._get_database_path()
        except Exception as exc:  # pragma: no cover - extremely rare
            return False, f"Failed to resolve database path: {exc}"

        if not path.exists():
            try:
                self._ensure_database_exists(path)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("Unable to create GeoIP sample dataset: %s", exc)
                return False, f"GeoIP database is missing: {exc}"

        return True, "GeoIPPlugin is configured"

    # ------------------------------------------------------------------
    # Public behaviour
    # ------------------------------------------------------------------
    def search_for_targets(self, search_term: str) -> List[Dict[str, str]]:
        """Return a list of candidate targets for the provided search term."""

        candidates = [
            {
                "targetId": ip,
                "targetName": ip,
                "pluginName": self.__class__.__name__,
            }
            for ip in self._iter_ips(search_term)
        ]
        logger.debug("GeoIPPlugin.search_for_targets produced %d results", len(candidates))
        return candidates

    def collect_locations(
        self,
        target: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LocationPoint]:
        """Return location information for ``target``."""

        ip = self._normalise_ip(target)
        if not ip:
            logger.debug("GeoIPPlugin.collect_locations ignored invalid target %r", target)
            return []

        if date_from or date_to:
            logger.debug(
                "GeoIPPlugin.collect_locations ignores date range (%s, %s) for %s",
                date_from,
                date_to,
                ip,
            )

        cached = self._cache.get(ip)
        if cached:
            return [replace(cached, timestamp=datetime.utcnow())]

        dataset_point = self._lookup_from_dataset(ip)
        if dataset_point:
            self._cache[ip] = dataset_point
            return [replace(dataset_point, timestamp=datetime.utcnow())]

        derived = self._derive_location(ip)
        self._cache[ip] = derived
        return [replace(derived, timestamp=datetime.utcnow())]

    def run(self, target: str) -> List[LocationPoint]:
        return self.collect_locations(target)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_database_path(self) -> Path:
        configured = self.config.get("database_path") or str(self._default_database_path)
        return Path(str(configured)).expanduser()

    def _ensure_database_exists(self, path: Optional[Path] = None) -> None:
        if path is None:
            path = self._get_database_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return

        sample_path = (
            Path(__file__).resolve().parents[2]
            / "resources"
            / "samples"
            / "geoip_sample.csv"
        )

        if sample_path.exists():
            shutil.copyfile(sample_path, path)
            logger.info("Copied GeoIP sample dataset to %s", path)
            return

        # Fallback: create a dataset from the built-in known IPs.
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["ip_start", "ip_end", "latitude", "longitude", "city", "region", "country"])
            for ip, (lat, lon, context) in self._KNOWN_IPS.items():
                writer.writerow([ip, ip, lat, lon, context, "", ""])
        logger.info("Generated minimal GeoIP dataset at %s", path)

    def _load_database(self) -> None:
        path = self._get_database_path()
        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            self._ensure_database_exists(path)
            mtime = path.stat().st_mtime

        if self._database_path == path and self._database_mtime == mtime:
            return

        with self._lock:
            if self._database_path == path and self._database_mtime == mtime:
                return

            range_starts: List[int] = []
            ranges: List[Tuple[int, int, float, float, str]] = []

            with path.open("r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    try:
                        start_ip = ipaddress.ip_address(row["ip_start"].strip())
                        end_ip = ipaddress.ip_address((row.get("ip_end") or row["ip_start"]).strip())
                        latitude = float(row["latitude"])
                        longitude = float(row["longitude"])
                        context_parts = [
                            row.get("city", "").strip(),
                            row.get("region", "").strip(),
                            row.get("country", "").strip(),
                        ]
                        context = ", ".join(part for part in context_parts if part)
                        if not context:
                            context = "GeoIP offline dataset"
                    except Exception as exc:
                        logger.debug("Skipping GeoIP row due to %s: %s", exc, row)
                        continue

                    start_int = int(start_ip)
                    end_int = int(end_ip)
                    if end_int < start_int:
                        start_int, end_int = end_int, start_int

                    range_starts.append(start_int)
                    ranges.append((start_int, end_int, latitude, longitude, context))

            combined = sorted(zip(range_starts, ranges), key=lambda item: item[0])
            self._range_starts = [item[0] for item in combined]
            self._ranges = [item[1] for item in combined]
            self._database_path = path
            self._database_mtime = mtime
            self._cache.clear()
            logger.info("Loaded %d GeoIP ranges from %s", len(self._ranges), path)

    def _lookup_from_dataset(self, ip: str) -> Optional[LocationPoint]:
        self._load_database()
        if not self._ranges:
            return None

        ip_int = int(ipaddress.ip_address(ip))
        index = bisect_right(self._range_starts, ip_int) - 1
        if index < 0:
            return None

        start_int, end_int, latitude, longitude, context = self._ranges[index]
        if not (start_int <= ip_int <= end_int):
            return None

        return LocationPoint(
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.utcnow(),
            source="GeoIP (offline)",
            context=context or f"Offline lookup for {ip}",
        )

    @staticmethod
    def _iter_ips(search_term: str) -> Iterable[str]:
        separators = {",", "\n", "\r", "\t", " "}
        parts: List[str] = [search_term]
        for separator in separators:
            parts = [sub for part in parts for sub in part.split(separator)]
        for part in parts:
            normalised = GeoIPPlugin._normalise_ip(part)
            if normalised:
                yield normalised

    @staticmethod
    def _normalise_ip(candidate: str) -> Optional[str]:
        try:
            return str(ipaddress.ip_address(candidate.strip()))
        except (ValueError, AttributeError):
            return None

    def _derive_location(self, ip: str) -> LocationPoint:
        """Generate deterministic pseudo coordinates for unknown IP addresses."""

        address = ipaddress.ip_address(ip)
        integer_value = int(address)
        precision = int(self.config.get("fallback_precision", 2) or 0)
        precision = max(0, min(6, precision))

        latitude = ((integer_value % 1800000) / 10000.0) - 90.0
        longitude = (((integer_value // 1800000) % 3600000) / 10000.0) - 180.0
        latitude = round(latitude, precision)
        longitude = round(longitude, precision)

        return LocationPoint(
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.utcnow(),
            source="GeoIP (derived)",
            context=f"Derived fallback for {ip}",
        )


__all__ = ["GeoIPPlugin"]
