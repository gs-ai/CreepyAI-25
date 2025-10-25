"""Shared utilities for social media archive plugins."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple

from app.plugins.base_plugin import BasePlugin


class ArchiveSocialMediaPlugin(BasePlugin):
    """Base class for plugins that ingest exported social media archives."""

    def __init__(self, *, name: str, description: str, temp_subdir: str) -> None:
        super().__init__(name=name, description=description)
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

