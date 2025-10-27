"""Unit tests for the plugin manager."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from app.plugins.plugin_manager import PluginManager


class SamplePlugin:
    def run(self) -> str:
        return "sample"

    def get_info(self) -> dict[str, Any]:  # pragma: no cover - simple accessor
        return {"name": "Sample Plugin"}


class BadPlugin:
    def __init__(self) -> None:
        raise RuntimeError("bad news")

    def get_info(self) -> dict[str, Any]:  # pragma: no cover - defensive
        return {"name": "Bad"}


def test_register_and_execute() -> None:
    pm = PluginManager()
    pm.initialize()

    pm.register_plugins([SamplePlugin])

    assert pm.execute_plugin("SamplePlugin") == "sample"
    assert pm.execute_plugin("Sample Plugin") == "sample"
    assert pm.execute_plugin("Unknown") is None


def test_failed_plugin_registration(caplog: pytest.LogCaptureFixture) -> None:
    pm = PluginManager()
    pm.initialize()

    with caplog.at_level("ERROR"):
        pm.register_plugins([BadPlugin])

    failures = pm.get_failed_plugins()
    assert "BadPlugin" in failures
    assert failures["BadPlugin"].startswith("RuntimeError")
    assert any("Failed to instantiate plugin" in message for message in caplog.messages)
