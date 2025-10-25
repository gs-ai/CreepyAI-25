"""Utilities for persisting and loading local LLM analysis history."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import List, Mapping, MutableMapping, Optional

from app.core.path_utils import get_user_data_dir

logger = logging.getLogger(__name__)


@dataclass
class AnalysisHistoryEntry:
    """A single persisted analysis run."""

    subject: str
    created_at: datetime
    integrity: str
    file_path: Path
    payload: Mapping[str, object]

    def label(self) -> str:
        focus = self.payload.get("focus")
        focus_part = f" – {focus}" if focus else ""
        timestamp = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"{timestamp} | {self.subject}{focus_part}"


def get_default_history_dir(base_dir: Optional[Path] = None) -> Path:
    """Return the default directory used to store analysis history."""

    if base_dir is None:
        base_dir = get_user_data_dir()
    directory = Path(base_dir) / "analysis_history"
    return directory


def persist_analysis_result(directory: Path, payload: Mapping[str, object]) -> AnalysisHistoryEntry:
    """Persist the payload to disk with an integrity hash."""

    directory.mkdir(parents=True, exist_ok=True)

    prepared_payload: MutableMapping[str, object] = dict(payload)
    prepared_payload.pop("history_path", None)

    generated_at = _parse_datetime(str(prepared_payload.get("generated_at") or ""))
    if not generated_at:
        generated_at = datetime.utcnow()
        prepared_payload["generated_at"] = generated_at.isoformat()

    digest = _compute_integrity(prepared_payload)
    integrity = f"sha256:{digest}"
    prepared_payload["integrity"] = integrity

    subject = str(prepared_payload.get("subject") or "analysis")
    filename = _build_history_filename(subject, generated_at, digest)
    file_path = directory / filename

    try:
        file_path.write_text(json.dumps(prepared_payload, indent=2, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        logger.error("Unable to persist analysis history to %s: %s", file_path, exc)
        raise

    return AnalysisHistoryEntry(
        subject=subject,
        created_at=generated_at,
        integrity=integrity,
        file_path=file_path,
        payload=prepared_payload,
    )


def load_recent_history(directory: Path, limit: int = 10) -> List[AnalysisHistoryEntry]:
    """Load recent analysis entries from disk."""

    if not directory.exists():
        return []

    entries: List[AnalysisHistoryEntry] = []
    for path in sorted(directory.glob("*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping unreadable analysis history %s: %s", path, exc)
            continue

        created_at = _parse_datetime(str(payload.get("generated_at") or ""))
        if not created_at:
            created_at = datetime.utcnow()
            payload["generated_at"] = created_at.isoformat()

        integrity = str(payload.get("integrity") or "")
        digest = _compute_integrity(payload)
        expected = f"sha256:{digest}"
        if integrity != expected:
            logger.warning(
                "History integrity mismatch for %s (expected %s, saw %s)",
                path,
                expected,
                integrity,
            )
            payload["integrity"] = expected
            integrity = expected

        entries.append(
            AnalysisHistoryEntry(
                subject=str(payload.get("subject") or "analysis"),
                created_at=created_at,
                integrity=integrity,
                file_path=path,
                payload=payload,
            )
        )

    entries.sort(key=lambda item: item.created_at, reverse=True)
    if limit:
        entries = entries[:limit]
    return entries


def _compute_integrity(payload: Mapping[str, object]) -> str:
    """Compute a deterministic SHA-256 hash for the payload."""

    serialisable = _normalise_payload(payload)
    serialised = json.dumps(serialisable, sort_keys=True, separators=(",", ":"))
    return sha256(serialised.encode("utf-8")).hexdigest()


def _normalise_payload(payload: Mapping[str, object]) -> Mapping[str, object]:
    """Remove volatile fields before hashing."""

    if isinstance(payload, dict):
        cleaned: MutableMapping[str, object] = {}
        for key, value in payload.items():
            if key in {"integrity", "history_path"}:
                continue
            cleaned[key] = _normalise_payload(value) if isinstance(value, dict) else value
        return cleaned
    if isinstance(payload, list):  # type: ignore[unreachable]
        return [_normalise_payload(item) if isinstance(item, dict) else item for item in payload]  # type: ignore[return-value]
    return payload


def _build_history_filename(subject: str, created_at: datetime, digest: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", subject.lower()).strip("-") or "analysis"
    timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}_{slug}_{digest[:12]}.json"


def _parse_datetime(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


__all__ = [
    "AnalysisHistoryEntry",
    "get_default_history_dir",
    "persist_analysis_result",
    "load_recent_history",
]
