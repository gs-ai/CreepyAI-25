from pathlib import Path

import pytest

from app.core.plugins import PluginManager
from app.plugins.catalog import PluginCatalog


@pytest.fixture()
def sample_plugin_dir(tmp_path: Path) -> Path:
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "sample_plugin.py"
    plugin_file.write_text(
        """
from app.plugins.base_plugin import BasePlugin


class SamplePlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__("Sample", "Sample plugin for testing")

    def collect_locations(self, target, date_from=None, date_to=None):
        return []
""",
        encoding="utf-8",
    )
    return plugin_dir


def test_plugin_catalog_caches_manifest(tmp_path: Path, sample_plugin_dir: Path) -> None:
    cache_path = tmp_path / "catalog.json"
    catalog = PluginCatalog([sample_plugin_dir], cache_path=cache_path)

    descriptors = catalog.load(force_refresh=True)
    assert descriptors
    identifiers = {descriptor.identifier for descriptor in descriptors}
    assert "sample_plugin" in identifiers

    first_mtime = cache_path.stat().st_mtime_ns
    again = catalog.load()
    second_mtime = cache_path.stat().st_mtime_ns

    assert first_mtime == second_mtime
    assert identifiers == {descriptor.identifier for descriptor in again}


def test_core_plugin_manager_uses_catalog(tmp_path: Path, sample_plugin_dir: Path) -> None:
    manager = PluginManager()
    manager.add_plugin_directory(str(sample_plugin_dir))
    manager.discover_plugins(force_refresh=True)

    assert "sample_plugin" in manager.plugins

    manifest = manager.get_manifest()
    assert "sample_plugin" in manifest
    assert manifest["sample_plugin"]["info"]["name"] == "Sample"

    failed = manager.get_failed_plugins()
    for key, value in failed.items():
        assert key
        assert value
