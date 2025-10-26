"""Unit tests for the CreepyAI engine.

These tests cover basic initialisation and plugin execution flows. The
tests use a dummy plugin implementation to avoid dependencies on
external data or plugins.
"""

from __future__ import annotations

import unittest
from typing import Any

from app.core.engine import Engine


class DummyPlugin:
    """Simple plugin used for testing the engine."""

    def __init__(self) -> None:
        self.ran_with: tuple[Any, dict[str, Any]] | None = None

    def run(self, *args: Any, **kwargs: Any) -> str:
        self.ran_with = (args, kwargs)
        return "ok"

    def get_info(self) -> dict[str, Any]:
        return {"name": "DummyPlugin"}


class EngineTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = Engine()
        self.engine.initialize({"plugins": {"enabled": False}})

    def test_run_plugin_missing(self) -> None:
        result = self.engine.run_plugin("nonexistent")
        self.assertIsNone(result)

    def test_run_plugin_success(self) -> None:
        # Register dummy plugin manually
        from app.plugins.plugin_manager import PluginManager

        pm = PluginManager()
        pm.register_plugins([DummyPlugin])
        self.engine.plugin_manager = pm
        result = self.engine.run_plugin("DummyPlugin")
        self.assertEqual(result, "ok")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()