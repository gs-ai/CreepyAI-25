"""Unit tests for the CreepyAI engine."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from app.core.engine import Engine
from app.plugins.plugin_manager import PluginManager


class DummyPlugin:
    def __init__(self) -> None:
        self.ran_with: tuple[tuple[Any, ...], dict[str, Any]] | None = None

    def run(self, *args: Any, **kwargs: Any) -> str:
        self.ran_with = (args, kwargs)
        return "ok"

    def get_info(self) -> dict[str, Any]:
        return {"name": "Dummy Plugin"}


class ExplodingPlugin:
    def run(self) -> None:
        raise RuntimeError("boom")

    def get_info(self) -> dict[str, Any]:  # pragma: no cover - simple accessor
        return {"name": "Exploder"}


@pytest.fixture(autouse=True)
def reset_engine_singleton() -> None:
    engine = Engine()
    engine.reset()


def _prepare_engine_with_plugins(*plugins: type) -> Engine:
    engine = Engine()
    engine.initialize({"plugins": {"enabled": False}})
    manager = PluginManager()
    manager.initialize()
    manager.register_plugins(list(plugins))
    engine.set_plugin_manager(manager)
    return engine


def test_run_plugin_success() -> None:
    engine = _prepare_engine_with_plugins(DummyPlugin)

    result = engine.run_plugin("DummyPlugin")

    assert result == "ok"


def test_run_plugin_unknown_returns_none(caplog: pytest.LogCaptureFixture) -> None:
    engine = _prepare_engine_with_plugins(DummyPlugin)

    with caplog.at_level("ERROR"):
        result = engine.run_plugin("missing")

    assert result is None
    assert any("not found" in message for message in caplog.messages)


def test_run_plugin_handles_exceptions(caplog: pytest.LogCaptureFixture) -> None:
    engine = _prepare_engine_with_plugins(ExplodingPlugin)

    with caplog.at_level("ERROR"):
        result = engine.run_plugin("ExplodingPlugin")

    assert result is None
    assert any("Error executing plugin" in record for record in caplog.messages)
