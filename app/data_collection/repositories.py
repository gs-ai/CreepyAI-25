"""Repository helpers that power offline social media lookups."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence

logger = logging.getLogger(__name__)


class DataRepository:
    """Interface for retrieving location records for a plugin."""

    def search(self, slug: str, term: str) -> Sequence[Mapping[str, object]]:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class StaticJSONRepository(DataRepository):
    """Load curated social media locations from a JSON dataset."""

    dataset_path: Path

    def __post_init__(self) -> None:
        self._records_by_slug: Dict[str, List[Mapping[str, object]]] = {}
        self._index_terms: Dict[str, Dict[str, List[Mapping[str, object]]]] = {}
        self._load()

    def search(self, slug: str, term: str) -> Sequence[Mapping[str, object]]:
        term_key = term.casefold().strip()
        if not term_key:
            return tuple(self._records_by_slug.get(slug, ()))

        slug_terms = self._index_terms.get(slug)
        if not slug_terms:
            return ()

        results = slug_terms.get(term_key)
        if results is not None:
            return tuple(results)

        # Fallback to contains search for partial matches
        matches: List[Mapping[str, object]] = []
        for candidate_term, candidate_records in slug_terms.items():
            if term_key in candidate_term or candidate_term in term_key:
                matches.extend(candidate_records)
        return tuple(matches)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load(self) -> None:
        try:
            payload = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            logger.debug("Static dataset not found: %s", self.dataset_path)
            return
        except json.JSONDecodeError as exc:
            logger.warning("Invalid JSON dataset %s: %s", self.dataset_path, exc)
            return

        if not isinstance(payload, Mapping):
            logger.warning("Unexpected dataset structure in %s", self.dataset_path)
            return

        for slug, entries in payload.items():
            if not isinstance(entries, Iterable):
                continue

            normalized_slug = str(slug)
            slug_records: List[Mapping[str, object]] = []
            slug_terms: MutableMapping[str, List[Mapping[str, object]]] = {}

            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue

                record = self._normalize_entry(entry)
                if record is None:
                    continue

                slug_records.append(record)

                terms = entry.get("terms")
                term_values: Iterable[str]
                if isinstance(terms, str):
                    term_values = [terms]
                elif isinstance(terms, Iterable):
                    term_values = [str(term) for term in terms if str(term).strip()]
                else:
                    term_values = []

                for term_value in term_values:
                    slug_terms.setdefault(term_value.casefold().strip(), []).append(record)

            self._records_by_slug[normalized_slug] = slug_records
            self._index_terms[normalized_slug] = dict(slug_terms)

    def _normalize_entry(self, entry: Mapping[str, object]) -> Optional[Mapping[str, object]]:
        try:
            latitude = float(entry["latitude"])  # type: ignore[index]
            longitude = float(entry["longitude"])  # type: ignore[index]
        except (KeyError, TypeError, ValueError):
            return None

        name = str(entry.get("name") or "")
        display_name = str(entry.get("display_name") or name)
        category = entry.get("category")
        source_id = entry.get("source_id")
        source = entry.get("source")

        normalized: Dict[str, object] = {
            "lat": latitude,
            "lon": longitude,
            "name": name,
            "display_name": display_name,
            "type": category,
        }

        if category is not None:
            normalized["category"] = category

        if source_id is not None:
            normalized["source_id"] = source_id

        if source is not None:
            normalized["source"] = source

        return normalized


__all__ = ["DataRepository", "StaticJSONRepository"]
