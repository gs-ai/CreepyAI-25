"""Tools for collecting public social media location datasets."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

import requests

from app.plugins.social_media import SOCIAL_MEDIA_PLUGINS

logger = logging.getLogger(__name__)


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


@dataclass
class CollectionResult:
    """Represents a single collected location entry."""

    source_id: str
    latitude: float
    longitude: float
    name: str
    category: Optional[str]
    display_name: Optional[str]
    source: str
    collected_at: datetime
    raw: Mapping[str, object] = field(default_factory=dict)

    def to_json(self) -> Dict[str, object]:
        return {
            "source_id": self.source_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "name": self.name,
            "category": self.category,
            "display_name": self.display_name,
            "source": self.source,
            "collected_at": self.collected_at.isoformat(),
            "raw": self.raw,
        }


class SocialMediaDataCollector:
    """Collect publicly available location data for social media plugins."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        fetcher: Optional[Callable[[str], Sequence[Mapping[str, object]]]] = None,
    ) -> None:
        self.session = session or requests.Session()
        self.session.headers.setdefault(
            "User-Agent",
            "CreepyAI-SocialMediaCollector/1.0 (+https://github.com/creepyai)",
        )
        self._fetcher = fetcher or self._fetch_from_nominatim

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def collect(self, plugin_slugs: Optional[Iterable[str]] = None) -> Dict[str, Path]:
        """Collect data for the selected plugin slugs.

        Returns a mapping of plugin slugs to the dataset paths written.
        """

        results: Dict[str, Path] = {}

        from app.plugins.social_media.base import ArchiveSocialMediaPlugin

        registry = SOCIAL_MEDIA_PLUGINS
        if plugin_slugs is not None:
            registry = {slug: registry[slug] for slug in plugin_slugs if slug in registry}

        timestamp = datetime.now(timezone.utc)

        for slug, plugin_cls in registry.items():
            plugin: ArchiveSocialMediaPlugin = plugin_cls()
            dataset_path = Path(plugin.get_data_directory()) / plugin.dataset_filename
            dataset_path.parent.mkdir(parents=True, exist_ok=True)

            search_terms = list(plugin.collection_terms) or [plugin.name]

            collected_records: MutableMapping[str, CollectionResult] = {
                entry.source_id: entry
                for entry in self._load_existing_records(dataset_path)
            }

            for term in search_terms:
                try:
                    raw_results = self._fetcher(term)
                except Exception as exc:  # pragma: no cover - defensive logging
                    logger.warning("Failed to fetch results for %s (%s): %s", slug, term, exc)
                    continue

                for raw in raw_results:
                    record = self._convert_raw_record(
                        raw, plugin.data_source_url or plugin.name, timestamp
                    )
                    if record is None:
                        continue

                    stored = collected_records.get(record.source_id)
                    if stored is None or stored.collected_at <= record.collected_at:
                        collected_records[record.source_id] = record

            payload = {
                "metadata": {
                    "plugin": plugin.name,
                    "slug": slug,
                    "updated_at": timestamp.isoformat(),
                    "terms": search_terms,
                    "source": plugin.data_source_url or "openstreetmap",
                },
                "records": [
                    entry.to_json()
                    for entry in sorted(
                        collected_records.values(),
                        key=lambda item: (item.collected_at, item.source_id),
                        reverse=True,
                    )
                ],
            }

            dataset_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            results[slug] = dataset_path

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _fetch_from_nominatim(self, query: str) -> Sequence[Mapping[str, object]]:
        logger.debug("Fetching Nominatim results for %s", query)
        response = self.session.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 25,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def _load_existing_records(self, dataset_path: Path) -> List[CollectionResult]:
        if not dataset_path.exists():
            return []

        try:
            payload = json.loads(dataset_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Unable to read existing dataset %s: %s", dataset_path, exc)
            return []

        records = payload.get("records") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            return []

        parsed: List[CollectionResult] = []
        for record in records:
            if not isinstance(record, dict):
                continue

            try:
                collected_at = datetime.fromisoformat(record["collected_at"])
            except Exception:  # pragma: no cover - invalid timestamps
                collected_at = datetime.now(timezone.utc)

            try:
                parsed.append(
                    CollectionResult(
                        source_id=str(record["source_id"]),
                        latitude=float(record["latitude"]),
                        longitude=float(record["longitude"]),
                        name=str(record.get("name") or ""),
                        category=record.get("category"),
                        display_name=record.get("display_name"),
                        source=str(record.get("source") or ""),
                        collected_at=collected_at,
                        raw=record.get("raw") or {},
                    )
                )
            except (KeyError, TypeError, ValueError):  # pragma: no cover - defensive
                continue

        return parsed

    def _convert_raw_record(
        self,
        raw: Mapping[str, object],
        source: str,
        collected_at: datetime,
    ) -> Optional[CollectionResult]:
        try:
            latitude = float(raw["lat"])  # type: ignore[index]
            longitude = float(raw["lon"])  # type: ignore[index]
        except (KeyError, TypeError, ValueError):
            return None

        osm_type = str(raw.get("osm_type") or "")
        osm_id = raw.get("osm_id")
        if osm_type and osm_id is not None:
            source_id = f"{osm_type}:{osm_id}"
        else:
            source_id = f"{source}:{latitude:.6f},{longitude:.6f}"

        name = str(raw.get("name") or raw.get("display_name") or source)
        category = str(raw.get("type") or raw.get("category") or "") or None
        display_name = str(raw.get("display_name") or "") or None

        return CollectionResult(
            source_id=source_id,
            latitude=latitude,
            longitude=longitude,
            name=name,
            category=category,
            display_name=display_name,
            source=source,
            collected_at=collected_at,
            raw=raw,
        )


__all__ = ["SocialMediaDataCollector", "CollectionResult"]

