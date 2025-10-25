#!/usr/bin/env python
"""CLI entry point for collecting public social media location datasets."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Iterable, Optional

from app.data_collection.social_media_data_collector import SocialMediaDataCollector
from app.plugins.social_media import SOCIAL_MEDIA_PLUGINS


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect publicly available social media locations and store them in the "
            "managed plugin directories."
        )
    )
    parser.add_argument(
        "--plugins",
        nargs="*",
        metavar="SLUG",
        help="Limit collection to specific social media plugin slugs",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    collector = SocialMediaDataCollector()
    slugs = args.plugins

    if slugs:
        unknown = sorted(set(slugs) - set(SOCIAL_MEDIA_PLUGINS))
        if unknown:
            logging.error("Unknown plugin slugs requested: %s", ", ".join(unknown))
            return 1

    results = collector.collect(slugs)

    if not results:
        logging.warning("No datasets collected")
        return 0

    for slug, path in sorted(results.items()):
        logging.info("%s dataset written to %s", slug, path)

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())

