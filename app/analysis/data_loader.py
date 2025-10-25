from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from app.plugins.social_media import SOCIAL_MEDIA_PLUGINS

logger = logging.getLogger(__name__)


@dataclass
class LocationRecord:
    """Normalised view of a location record emitted by CreepyAI-25 plugins."""

    plugin: str
    slug: str
    dataset_path: Path
    source_id: str
    latitude: float
    longitude: float
    name: str
    category: Optional[str]
    display_name: Optional[str]
    collected_at: datetime
    source: str
    raw: Dict[str, object]

    def to_prompt_dict(self) -> Dict[str, object]:
        return {
            "plugin": self.plugin,
            "slug": self.slug,
            "source_id": self.source_id,
            "name": self.name,
            "category": self.category,
            "display_name": self.display_name,
            "source": self.source,
            "collected_at": self.collected_at.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


def load_social_media_records(
    *,
    limit_per_plugin: Optional[int] = None,
    include_empty: bool = False,
) -> List[LocationRecord]:
    """Load curated social media datasets prepared for CreepyAI-25 plugins."""

    records: List[LocationRecord] = []

    from app.plugins.social_media.base import ArchiveSocialMediaPlugin

    for slug, plugin_cls in SOCIAL_MEDIA_PLUGINS.items():
        plugin: ArchiveSocialMediaPlugin = plugin_cls()
        dataset_path = Path(plugin.get_data_directory()) / plugin.dataset_filename

        if not dataset_path.exists():
            if include_empty:
                logger.info("Dataset for %s is missing at %s", slug, dataset_path)
            continue

        try:
            payload = json.loads(dataset_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Unable to load dataset for %s (%s): %s", slug, dataset_path, exc)
            continue

        entries = _extract_records_from_payload(payload)
        if not entries:
            if include_empty:
                logger.info("Dataset for %s is empty", slug)
            continue

        if limit_per_plugin is not None:
            entries = entries[: limit_per_plugin]

        records.extend(
            LocationRecord(
                plugin=plugin.name,
                slug=slug,
                dataset_path=dataset_path,
                source_id=entry["source_id"],
                latitude=entry["latitude"],
                longitude=entry["longitude"],
                name=entry.get("name") or "",
                category=entry.get("category"),
                display_name=entry.get("display_name"),
                collected_at=_parse_datetime(entry.get("collected_at")),
                source=entry.get("source") or plugin.data_source_url or "",
                raw=entry.get("raw") or {},
            )
            for entry in entries
        )

    records.sort(key=lambda record: record.collected_at, reverse=True)
    return records


def _extract_records_from_payload(payload: object) -> List[Dict[str, object]]:
    if isinstance(payload, dict):
        raw_records = payload.get("records", [])
    else:
        raw_records = payload

    if not isinstance(raw_records, Sequence):
        return []

    parsed: List[Dict[str, object]] = []
    for entry in raw_records:
        if not isinstance(entry, dict):
            continue
        try:
            parsed.append(
                {
                    "source_id": str(entry["source_id"]),
                    "latitude": float(entry["latitude"]),
                    "longitude": float(entry["longitude"]),
                    "name": entry.get("name"),
                    "category": entry.get("category"),
                    "display_name": entry.get("display_name"),
                    "source": entry.get("source"),
                    "collected_at": entry.get("collected_at"),
                    "raw": entry.get("raw") or {},
                }
            )
        except (KeyError, TypeError, ValueError):
            continue

    parsed.sort(
        key=lambda entry: _parse_datetime(entry.get("collected_at")),
        reverse=True,
    )
    return parsed


def _parse_datetime(value: Optional[str]) -> datetime:
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.min


__all__ = ["LocationRecord", "load_social_media_records"]
