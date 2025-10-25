#!/usr/bin/env python3
"""Utility script that removes legacy plugin files after categorisation.

Enhancements:

* Fully parameterised CLI (``--plugins-dir``, ``--dry-run``, ``--yes``) so the
  script can be used in automated pipelines.
* Improved verification that reports missing plugins rather than just failing.
* Logging that indicates exactly which files were deleted or skipped.
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Tuple


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


DEFAULT_CATEGORIES: Sequence[str] = (
    "social_media",
    "location_services",
    "data_extraction",
    "tools",
    "other",
)


@dataclass
class VerificationResult:
    categorized: bool
    missing_plugins: Tuple[str, ...]


def iter_python_files(directory: Path) -> Iterable[Path]:
    return (path for path in directory.iterdir() if path.suffix == ".py" and not path.name.startswith("__"))


def verify_categorized_plugins(plugins_dir: Path, categories: Sequence[str]) -> VerificationResult:
    """Check that every plugin in ``plugins_dir`` exists in a category."""

    originals = {path.name for path in iter_python_files(plugins_dir)}

    categorized = set()
    for category in categories:
        category_dir = plugins_dir / category
        if not category_dir.is_dir():
            continue
        categorized.update(path.name for path in iter_python_files(category_dir))

    missing = tuple(sorted(originals - categorized))
    return VerificationResult(categorized=not missing, missing_plugins=missing)


def cleanup_original_plugins(
    plugins_dir: Path,
    categories: Sequence[str],
    assume_yes: bool,
    dry_run: bool,
) -> bool:
    originals = sorted(iter_python_files(plugins_dir))
    if not originals:
        logger.info("No original plugin files found to clean up.")
        return True

    verification = verify_categorized_plugins(plugins_dir, categories)
    if not verification.categorized:
        logger.error("Cannot remove original plugins. Missing categorised copies: %s", ", ".join(verification.missing_plugins))
        return False

    logger.info("Located %s original plugin file%s", len(originals), "s" if len(originals) != 1 else "")
    if dry_run:
        for path in originals:
            logger.info("[dry-run] Would remove %s", path)
        return True

    if not assume_yes:
        print("This will delete the following plugin files:")
        for path in originals:
            print(f"  - {path.name}")
        response = input("\nProceed? (yes/no): ").strip().lower()
        if response not in {"y", "yes"}:
            logger.info("Operation cancelled by user")
            return False

    for path in originals:
        try:
            path.unlink()
            logger.info("Removed %s", path.name)
        except Exception as exc:  # pragma: no cover - filesystem dependent
            logger.error("Failed to remove %s: %s", path, exc)
            return False

    logger.info("Original plugin files removed successfully")
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean up uncategorised plugin files")
    parser.add_argument("--plugins-dir", type=Path, default=Path("app/plugins"), help="Root plugins directory")
    parser.add_argument(
        "--categories",
        nargs="*",
        default=list(DEFAULT_CATEGORIES),
        help="Expected category subdirectories (defaults match project layout)",
    )
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without deleting files")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    plugins_dir: Path = args.plugins_dir.resolve()
    if not plugins_dir.exists():
        logger.error("Plugins directory does not exist: %s", plugins_dir)
        return 1

    success = cleanup_original_plugins(
        plugins_dir=plugins_dir,
        categories=tuple(args.categories),
        assume_yes=args.yes,
        dry_run=args.dry_run,
    )
    return 0 if success else 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
