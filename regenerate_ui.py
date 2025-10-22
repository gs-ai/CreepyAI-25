#!/usr/bin/env python3
"""Regenerate PyQt UI modules from ``.ui`` definitions."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def run_pyuic(input_path: Path, output_path: Path, pyuic_executable: str) -> None:
    command = [pyuic_executable, '-o', str(output_path), str(input_path)]
    logger.debug("Running %s", ' '.join(command))
    subprocess.run(command, check=True, capture_output=True, text=True)


def run_pyqt_fallback(input_path: Path, output_path: Path) -> None:
    from PyQt5 import uic  # type: ignore

    with output_path.open('w', encoding='utf-8') as fh:
        uic.compileUi(str(input_path), fh)


def regenerate_ui(input_path: Path, output_path: Path, pyuic_executable: str | None) -> bool:
    if not input_path.exists():
        logger.error("UI definition not found: %s", input_path)
        return False

    try:
        if pyuic_executable:
            run_pyuic(input_path, output_path, pyuic_executable)
        else:
            logger.info("pyuic executable not provided; falling back to PyQt5.uic.compileUi")
            run_pyqt_fallback(input_path, output_path)
        logger.info("UI file generated successfully: %s", output_path)
        return True
    except FileNotFoundError as exc:
        logger.warning("pyuic executable not found (%s). Attempting PyQt5 fallback.", exc)
        try:
            run_pyqt_fallback(input_path, output_path)
            logger.info("UI file generated successfully via PyQt fallback: %s", output_path)
            return True
        except Exception as fallback_exc:  # pragma: no cover - runtime guard
            logger.error("Fallback compilation failed: %s", fallback_exc)
            return False
    except subprocess.CalledProcessError as exc:
        logger.error("pyuic failed: %s", exc)
        logger.error("stdout: %s", exc.stdout)
        logger.error("stderr: %s", exc.stderr)
        return False
    except Exception as exc:  # pragma: no cover - runtime guard
        logger.error("Unexpected error: %s", exc)
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Regenerate PyQt UI modules")
    parser.add_argument("--input", type=Path, default=Path("app/gui/ui/creepyai_mainwindow.ui"), help="Input .ui file")
    parser.add_argument("--output", type=Path, default=Path("app/gui/ui/creepyai_mainwindow_ui.py"), help="Output Python file")
    parser.add_argument("--pyuic", help="Optional path to pyuic5 executable")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    success = regenerate_ui(args.input.resolve(), args.output.resolve(), args.pyuic)
    return 0 if success else 1


if __name__ == '__main__':  # pragma: no cover - CLI entry point
    sys.exit(main())
