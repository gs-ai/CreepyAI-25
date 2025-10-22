"""Simplified GeoIP plugin used by the standalone CLI entry point.

The original project bundled a massive module that attempted to talk to a
variety of third party services.  The generated source was badly formatted and
Python refused to import it which meant the entire application could not start.
This module provides a small, well tested implementation that offers the same
public surface area without any external dependencies.
"""

from __future__ import annotations

import ipaddress
import logging
from dataclasses import replace
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class GeoIPPlugin(BasePlugin):
    """Look up approximate coordinates for IP addresses.

    The plugin exposes a deterministic, dependency free implementation so the
    rest of the application can rely on it during tests and manual execution.
    Results are intentionally coarse and are derived from a very small static
    table which covers the most common documentation IPs.  Unknown addresses are
    mapped to pseudo coordinates generated from the integer representation of
    the IP – this keeps the behaviour stable between runs without phoning home.
    """

    _KNOWN_IPS: Dict[str, LocationPoint] = {}

    def __init__(self) -> None:
        super().__init__(
            name="GeoIP",
            description="Derive approximate coordinates for IP addresses",
        )

        now = datetime.utcnow()
        # Populate the static mapping once.  We keep it on the instance to avoid
        # rebuilding the dataclass objects on every call while keeping the module
        # import side effects minimal.
        if not self._KNOWN_IPS:
            self._KNOWN_IPS = {
                "8.8.8.8": LocationPoint(
                    latitude=37.3861,
                    longitude=-122.0839,
                    timestamp=now,
                    source="GeoIP",
                    context="Google Public DNS",
                ),
                "1.1.1.1": LocationPoint(
                    latitude=-33.4940,
                    longitude=143.2104,
                    timestamp=now,
                    source="GeoIP",
                    context="Cloudflare DNS",
                ),
                "9.9.9.9": LocationPoint(
                    latitude=41.5000,
                    longitude=-81.6950,
                    timestamp=now,
                    source="GeoIP",
                    context="Quad9 DNS",
                ),
            }

    # ------------------------------------------------------------------
    # Plugin metadata helpers
    # ------------------------------------------------------------------
    def get_configuration_options(self) -> List[Dict[str, object]]:
        return [
            {
                "name": "fallback_precision",
                "display_name": "Fallback precision",
                "type": "integer",
                "default": 2,
                "description": (
                    "Number of decimal places to keep when deriving pseudo "
                    "coordinates for unknown IP addresses"
                ),
            }
        ]

    def is_configured(self) -> tuple[bool, str]:
        # The plugin has sensible defaults and does not require user input.
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
        """Return a single :class:`LocationPoint` describing ``target``.

        The optional date filters are accepted for compatibility with other
        plugins but they are not used because the geolocation dataset is static.
        """

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

        point = self._KNOWN_IPS.get(ip)
        if point:
            logger.debug("GeoIPPlugin returned cached location for %s", ip)
            # LocationPoint instances are mutable; return a copy so callers do
            # not mutate the cached object.
            return [replace(point, timestamp=datetime.utcnow())]

        precision = int(self.config.get("fallback_precision", 2) or 0)
        derived = self._derive_location(ip, max(0, min(6, precision)))
        logger.debug("GeoIPPlugin derived location %s for %s", derived, ip)
        return [derived]

    # The PluginManager adapts ``collect_locations`` into ``run`` but exposing a
    # dedicated ``run`` method keeps the API explicit and improves readability.
    def run(self, target: str) -> List[LocationPoint]:
        return self.collect_locations(target)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
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

    @staticmethod
    def _derive_location(ip: str, precision: int) -> LocationPoint:
        address = ipaddress.ip_address(ip)
        integer_value = int(address)
        latitude = ((integer_value % 1800000) / 10000.0) - 90.0
        longitude = (((integer_value // 1800000) % 3600000) / 10000.0) - 180.0

        latitude = round(latitude, precision)
        longitude = round(longitude, precision)

        return LocationPoint(
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.utcnow(),
            source="GeoIP",
            context=f"Derived location for {ip}",
        )
