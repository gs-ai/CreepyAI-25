"""Unit tests for the plugin manager."""

from __future__ import annotations

import unittest
from typing import Any

from app.plugins.plugin_manager import PluginManager


class SamplePlugin:
    def __init__(self) -> None:
        pass
    def run(self) -> str:
        return "sample"
    def get_info(self) -> dict[str, Any]:
        return {"name": "Sample"}


class PluginManagerTestCase(unittest.TestCase):
    def test_register_and_execute(self) -> None:
        pm = PluginManager()
        pm.register_plugins([SamplePlugin])
        result = pm.execute_plugin("Sample")
        self.assertEqual(result, "sample")
        # Unknown plugin should return None
        self.assertIsNone(pm.execute_plugin("Unknown"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()