#!/usr/bin/env python3
"""Utility for downloading, normalising and maintaining icon assets.

This script originally downloaded a fixed list of social media favicons using
``urllib``.  The new implementation adds:

* A manifest driven workflow that allows additional icons to be supplied via a
  JSON or YAML file.
* Streaming downloads with ``requests`` for better error handling and HTTPS
  verification.
* Configurable resize targets, timeouts and retry logic.
* Structured logging output and explicit exit codes to support CI usage.

The default behaviour remains backwards compatible – running the script with no
arguments downloads the built-in icon list into ``app/resources/icons`` and
generates 64×64 PNG assets.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlparse

import requests
from requests import Response

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - yaml is optional but expected in the project
    yaml = None


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("icon_downloader")


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESOURCES_DIR = PROJECT_ROOT / "app" / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"


@dataclass(frozen=True)
class IconSource:
    """Represents a downloadable icon source."""

    name: str
    url: str

    def filename(self, extension: str = "png") -> str:
        return f"{self.name}-icon.{extension}"


DEFAULT_ICON_SOURCES: Mapping[str, str] = {
    "facebook": "https://www.facebook.com/favicon.ico",
    "instagram": "https://www.instagram.com/favicon.ico",
    "twitter": "https://twitter.com/favicon.ico",
    "linkedin": "https://www.linkedin.com/favicon.ico",
    "tiktok": "https://www.tiktok.com/favicon.ico",
    "snapchat": "https://www.snapchat.com/favicon.ico",
    "pinterest": "https://www.pinterest.com/favicon.ico",
    "yelp": "https://www.yelp.com/favicon.ico",
    "google": "https://www.google.com/favicon.ico",
    "maps": "https://maps.google.com/favicon.ico",
    "youtube": "https://www.youtube.com/favicon.ico",
    "reddit": "https://www.reddit.com/favicon.ico",
    "github": "https://github.com/favicon.ico",
}


def ensure_directory(path: Path) -> None:
    """Ensure ``path`` exists and is a directory."""

    path.mkdir(parents=True, exist_ok=True)


def _derive_suffix(url: str) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix
    return suffix if suffix else ".ico"


def _load_manifest(path: Path) -> MutableMapping[str, str]:
    """Load a manifest mapping icon names to URLs.

    Supported formats are JSON and YAML (if PyYAML is available).  The manifest
    must resolve to a mapping from icon names to URL strings.  Invalid entries
    are ignored with a warning so the script can continue downloading
    everything else.
    """

    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    data: MutableMapping[str, str]
    with path.open("r", encoding="utf-8") as fh:
        if path.suffix.lower() in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("PyYAML is required to load YAML manifests")
            loaded = yaml.safe_load(fh)
        else:
            loaded = json.load(fh)

    if not isinstance(loaded, Mapping):
        raise ValueError("Manifest must be a mapping of icon names to URLs")

    data = {}
    for key, value in loaded.items():
        if not isinstance(key, str) or not isinstance(value, str):
            logger.warning("Ignoring manifest entry %r -> %r (must be strings)", key, value)
            continue
        data[key.strip()] = value.strip()

    return data


def build_icon_sources(manifest: Optional[Path]) -> List[IconSource]:
    """Combine default icons with those provided in ``manifest``."""

    sources: Dict[str, str] = dict(DEFAULT_ICON_SOURCES)
    if manifest:
        try:
            manifest_data = _load_manifest(manifest)
        except Exception as exc:  # pragma: no cover - CLI path
            logger.error("Failed to load manifest %s: %s", manifest, exc)
            raise

        # Manifest entries override the defaults when they share a name
        sources.update(manifest_data)

    return [IconSource(name, url) for name, url in sorted(sources.items())]


def _stream_to_file(response: Response, destination: Path, chunk_size: int = 32_768) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as fh:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                fh.write(chunk)


def download_icon(
    session: requests.Session,
    source: IconSource,
    output_dir: Path,
    overwrite: bool,
    timeout: float,
    retries: int,
) -> Optional[Path]:
    """Download a single icon and return the resulting path.

    ``None`` is returned when the download ultimately fails.  Download failures
    are logged but do not raise by default to allow the script to continue with
    the rest of the manifest.  Retrying is handled with exponential backoff.
    """

    final_path = output_dir / source.filename("png")
    if final_path.exists() and not overwrite:
        logger.info("Icon for %s already exists, skipping", source.name)
        return final_path

    attempt = 0
    backoff = 1.0
    while attempt <= retries:
        attempt += 1
        try:
            logger.info("Downloading icon for %s from %s (attempt %s/%s)", source.name, source.url, attempt, retries + 1)
            response = session.get(source.url, timeout=timeout, stream=True)
            response.raise_for_status()
            suffix = _derive_suffix(source.url)
            download_target = output_dir / f"{source.name}{suffix}"
            _stream_to_file(response, download_target)
            logger.info("Saved icon to %s", download_target)
            return download_target
        except requests.RequestException as exc:
            if attempt > retries:
                logger.error("Failed to download icon for %s: %s", source.name, exc)
                return None
            logger.warning("Error downloading %s (attempt %s/%s): %s", source.name, attempt, retries + 1, exc)
            time.sleep(backoff)
            backoff *= 2


def convert_icon(input_path: Path) -> Path:
    """Convert ``input_path`` to PNG format in-place.

    Returns the path of the PNG file.  If the conversion fails or Pillow is not
    installed, ``input_path`` is returned unchanged.
    """

    if input_path.suffix.lower() == ".png":
        return input_path

    try:
        from PIL import Image  # type: ignore
    except ImportError:  # pragma: no cover - runtime guard
        logger.warning("Pillow not installed, skipping conversion for %s", input_path.name)
        return input_path

    filename = input_path.with_suffix(".png")
    try:
        with Image.open(input_path) as image:
            image.save(filename, "PNG")
    except Exception as exc:
        logger.error("Failed to convert %s to PNG: %s", input_path.name, exc)
        return input_path

    if filename != input_path:
        try:
            input_path.unlink(missing_ok=True)
        except AttributeError:  # pragma: no cover - Python <3.8 fallback
            if input_path.exists():
                input_path.unlink()

    return filename


def resize_icon(input_path: Path, size: Tuple[int, int]) -> bool:
    """Resize ``input_path`` to ``size`` using Pillow if available."""

    try:
        from PIL import Image  # type: ignore
    except ImportError:  # pragma: no cover - runtime guard
        logger.warning("Pillow not installed, skipping resize for %s", input_path.name)
        return False

    try:
        with Image.open(input_path) as image:
            if image.size == size:
                return True
            resized = image.resize(size, Image.LANCZOS)
            resized.save(input_path, optimize=True)
            logger.info("Resized %s to %sx%s", input_path.name, size[0], size[1])
            return True
    except Exception as exc:
        logger.error("Failed to resize %s: %s", input_path.name, exc)
        return False


def download_all_icons(
    output_dir: Path,
    overwrite: bool,
    resize: bool,
    size: Tuple[int, int],
    timeout: float,
    retries: int,
    manifest: Optional[Path] = None,
) -> List[Path]:
    """Download every icon described by the default list and ``manifest``."""

    ensure_directory(output_dir)
    session = requests.Session()
    session.headers.update({"User-Agent": "CreepyAI Icon Fetcher/1.0"})

    downloaded: List[Path] = []
    for source in build_icon_sources(manifest):
        path = download_icon(session, source, output_dir, overwrite, timeout, retries)
        if not path:
            continue
        target = convert_icon(path)
        if resize:
            resize_icon(target, size)
        path = target
        downloaded.append(path)

    session.close()
    return downloaded


def parse_size(value: str) -> Tuple[int, int]:
    try:
        width_str, height_str = value.lower().split("x", 1)
        width, height = int(width_str), int(height_str)
    except ValueError as exc:  # pragma: no cover - CLI guard
        raise argparse.ArgumentTypeError("Size must be WIDTHxHEIGHT, e.g. 64x64") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Size values must be positive integers")
    return width, height


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Download and prepare icon assets for CreepyAI")
    parser.add_argument("--output-dir", "-o", type=Path, default=ICONS_DIR, help="Directory to store icons")
    parser.add_argument("--manifest", "-m", type=Path, help="Optional JSON or YAML manifest of additional icons")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing icon files")
    parser.add_argument("--no-resize", action="store_true", help="Skip resizing icons to a square thumbnail")
    parser.add_argument("--size", type=parse_size, default=(64, 64), help="Resize target in WIDTHxHEIGHT format")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="Number of retry attempts per icon")

    args = parser.parse_args(argv)

    try:
        downloaded = download_all_icons(
            output_dir=args.output_dir,
            overwrite=args.overwrite,
            resize=not args.no_resize,
            size=args.size,
            timeout=args.timeout,
            retries=args.retries,
            manifest=args.manifest,
        )
    except Exception as exc:  # pragma: no cover - CLI path
        logger.error("Icon download failed: %s", exc)
        return 1

    if downloaded:
        logger.info("Downloaded %s icon%s", len(downloaded), "s" if len(downloaded) != 1 else "")
    else:
        logger.warning("No icons were downloaded – check the manifest or network connectivity")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
