"""Shared utilities for social media archive plugins."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)


class ArchiveSocialMediaPlugin(BasePlugin):
    """Base class for plugins that ingest exported social media archives."""

    data_source_url: str = ""
    collection_terms: Sequence[str] = ()
    dataset_filename: str = "collected_locations.json"

    def __init__(self, *, name: str, description: str, temp_subdir: str) -> None:
        directory_name = self.__class__.data_directory_name_from_source()
        super().__init__(
            name=name,
            description=description,
            data_directory_name=directory_name,
        )
        self._temp_subdir = temp_subdir

    # ------------------------------------------------------------------
    # BasePlugin overrides
    # ------------------------------------------------------------------
    def get_configuration_options(self) -> List[dict]:
        return []

    def is_configured(self) -> Tuple[bool, str]:
        if self.has_input_data():
            return True, f"{self.name} plugin is configured"

        data_dir = self.get_data_directory()
        return False, f"Add {self.name} exports to {data_dir}"

    # ------------------------------------------------------------------
    # Helpers for subclasses
    # ------------------------------------------------------------------
    @classmethod
    def data_directory_name_from_source(cls) -> str:
        url = cls.data_source_url.strip() if cls.data_source_url else ""
        if url:
            parsed = urlparse(url)
            host = parsed.netloc or parsed.path
            host = host.strip("/")
            if host:
                return host
        return cls.__name__.replace("Plugin", "").lower()

    def resolve_archive_root(self) -> Optional[Path]:
        """Return the prepared archive directory if data is available."""

        if not self.has_input_data():
            return None

        archive_path = Path(self.prepare_data_directory(self._temp_subdir))
        return archive_path if archive_path.exists() else None

    def iter_data_files(
        self, archive_root: Path, patterns: Iterable[str]
    ) -> Iterator[Path]:
        """Yield all files that match ``patterns`` within ``archive_root``."""

        root = archive_root if isinstance(archive_root, Path) else Path(archive_root)
        for pattern in patterns:
            yield from root.glob(pattern)

    # ------------------------------------------------------------------
    # Managed dataset helpers
    # ------------------------------------------------------------------
    def load_collected_locations(
        self,
        *,
        target: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Optional[List[LocationPoint]]:
        """Load collected location data stored in the managed directory.

        Returns ``None`` when the dataset file is missing so callers can
        gracefully fall back to archive processing.
        """

        dataset_path = Path(self.get_data_directory()) / self.dataset_filename
        if not dataset_path.exists():
            return None

        try:
            payload = json.loads(dataset_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to read collected dataset for %s: %s", self.name, exc)
            return []

        records = payload.get("records") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            logger.warning("Collected dataset for %s is not a list", self.name)
            return []

        points: List[LocationPoint] = []
        for record in records:
            if not isinstance(record, dict):
                continue

            try:
                latitude = float(record["latitude"])
                longitude = float(record["longitude"])
            except (KeyError, TypeError, ValueError):
                continue

            timestamp_value = record.get("collected_at") or record.get("timestamp")
            timestamp = self._parse_timestamp(timestamp_value)

            if timestamp is None:
                timestamp = datetime.now(timezone.utc)

            if date_from and timestamp < date_from:
                continue

            if date_to and timestamp > date_to:
                continue

            source = record.get("source") or self.name

            context_parts: List[str] = []
            for key in ("name", "category", "display_name"):
                value = record.get(key)
                if value:
                    context_parts.append(str(value))

            context = " | ".join(context_parts) if context_parts else source

            points.append(
                LocationPoint(
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=timestamp,
                    source=str(source),
                    context=context[:200],
                )
            )

        return points

    def _parse_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None

        candidates = [value]
        if isinstance(value, str) and value.endswith("Z"):
            candidates.append(value[:-1] + "+00:00")

        for candidate in candidates:
            try:
                parsed = datetime.fromisoformat(candidate)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed
            except ValueError:
                continue

        try:
            timestamp_float = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

        return datetime.fromtimestamp(timestamp_float, tz=timezone.utc)

