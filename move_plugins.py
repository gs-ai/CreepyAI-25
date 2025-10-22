#!/usr/bin/env python3
"""Organise CreepyAI plugins into category folders based on filename patterns."""

from __future__ import annotations

import argparse
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Mapping


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


DEFAULT_PATTERNS: Mapping[str, Iterable[str]] = {
    "social_media": (r"(facebook|twitter|instagram|linkedin|tiktok|snapchat|pinterest|yelp)", r"social_media"),
    "location_services": (r"(google_maps|foursquare|location_history|wifi_mapper|wifi_analysis)", r"geo[a-z]*", r"location"),
    "data_extraction": (r"(exif|google_takeout|idcrawl|email)", r"extract"),
    "tools": (r"(dummy|test|example|plugin_)", r"utils", r"tool"),
}


def parse_patterns(extra_patterns: Iterable[str]) -> Dict[str, List[str]]:
    patterns: Dict[str, List[str]] = {category: list(regexes) for category, regexes in DEFAULT_PATTERNS.items()}
    for entry in extra_patterns:
        if ':' not in entry:
            raise ValueError(f"Invalid pattern override '{entry}'. Use format 'category:regex'.")
        category, regex = entry.split(':', 1)
        patterns.setdefault(category, []).append(regex)
    return patterns


def categorize_plugins(plugins_dir: Path, pattern_map: Mapping[str, Iterable[str]]) -> Dict[str, List[Path]]:
    files = [path for path in plugins_dir.glob('*.py') if not path.name.startswith('__')]
    categories: Dict[str, List[Path]] = {category: [] for category in pattern_map}
    categories.setdefault('other', [])

    for plugin in files:
        assigned = False
        for category, patterns in pattern_map.items():
            if any(re.search(pattern, plugin.stem, re.IGNORECASE) for pattern in patterns):
                categories.setdefault(category, []).append(plugin)
                assigned = True
                break
        if not assigned:
            categories['other'].append(plugin)

    return categories


def ensure_category_init(category_dir: Path) -> None:
    init_file = category_dir / '__init__.py'
    if not init_file.exists():
        init_file.write_text(f'"""\nCreepyAI {category_dir.name.replace("_", " ").title()} Plugins\n"""\n', encoding='utf-8')


def organise_plugins(
    plugins_dir: Path,
    pattern_map: Mapping[str, Iterable[str]],
    mode: str,
    dry_run: bool,
) -> None:
    categories = categorize_plugins(plugins_dir, pattern_map)

    for category, plugins in categories.items():
        if not plugins:
            continue
        category_dir = plugins_dir / category
        if not dry_run:
            category_dir.mkdir(parents=True, exist_ok=True)
            ensure_category_init(category_dir)

        logger.info("%s %s plugin%s", mode.capitalize(), len(plugins), '' if len(plugins) == 1 else 's')
        for plugin in plugins:
            destination = category_dir / plugin.name
            if dry_run:
                logger.info("[dry-run] Would %s %s -> %s", mode, plugin.name, destination)
                continue

            if mode == 'copy':
                shutil.copy2(plugin, destination)
            elif mode == 'move':
                shutil.move(plugin, destination)
            elif mode == 'link':
                if destination.exists():
                    destination.unlink()
                destination.symlink_to(plugin.resolve())
            else:  # pragma: no cover - validated earlier
                raise ValueError(f"Unsupported mode: {mode}")



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organise CreepyAI plugins into category directories")
    parser.add_argument("--plugins-dir", type=Path, default=Path('app/plugins'), help="Root plugins directory")
    parser.add_argument("--mode", choices={'copy', 'move', 'link'}, default='copy', help="How to place plugins into categories")
    parser.add_argument("--dry-run", action='store_true', help="Only show actions without modifying files")
    parser.add_argument("--pattern", action='append', default=[], help="Additional category pattern override 'category:regex'")
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    plugins_dir = args.plugins_dir.resolve()
    if not plugins_dir.exists():
        logger.error("Plugins directory not found: %s", plugins_dir)
        return 1

    try:
        pattern_map = parse_patterns(args.pattern)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    organise_plugins(
        plugins_dir=plugins_dir,
        pattern_map=pattern_map,
        mode=args.mode,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        logger.info("Dry run complete. No files were modified.")
    else:
        logger.info("Plugin organisation complete using mode '%s'", args.mode)

    return 0


if __name__ == '__main__':  # pragma: no cover - CLI entry point
    raise SystemExit(main())
