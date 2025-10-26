from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def social_media_module(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    for module_name in list(sys.modules):
        if module_name.startswith("app.plugins.social_media") or module_name == "app.plugins.base_plugin":
            sys.modules.pop(module_name)

    module = importlib.import_module("app.plugins.social_media")
    return module, tmp_path


def test_social_media_registry_unique(social_media_module):
    module, _ = social_media_module
    from app.plugins.social_media.base import ArchiveSocialMediaPlugin

    registry = module.SOCIAL_MEDIA_PLUGINS
    assert len(registry) == len(set(registry.values()))

    for slug, cls in registry.items():
        assert slug == slug.lower()
        assert issubclass(cls, ArchiveSocialMediaPlugin)


def test_social_media_plugins_create_managed_directories(social_media_module):
    module, tmp_path = social_media_module

    imports_root = tmp_path / "creepyai" / "imports"

    for _, cls in module.SOCIAL_MEDIA_PLUGINS.items():
        plugin = cls()
        data_dir = Path(plugin.get_data_directory())
        assert data_dir.is_dir()
        assert data_dir.parent == imports_root
        assert not any(data_dir.iterdir())
        assert data_dir.name == cls.data_directory_name_from_source()


def test_social_media_plugins_load_collected_dataset(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    from app.plugins.social_media.facebook_plugin import FacebookPlugin

    plugin = FacebookPlugin()
    data_dir = Path(plugin.get_data_directory())
    dataset_path = data_dir / plugin.dataset_filename

    payload = {
        "metadata": {"updated_at": "2024-07-07T00:00:00+00:00"},
        "records": [
            {
                "source_id": "facebook:1",
                "latitude": 37.4848,
                "longitude": -122.1484,
                "name": "Meta HQ",
                "category": "office",
                "display_name": "Meta Headquarters, Menlo Park",
                "source": "https://www.facebook.com",
                "collected_at": "2024-07-07T12:00:00+00:00",
            }
        ],
    }

    dataset_path.write_text(json.dumps(payload), encoding="utf-8")

    results = plugin.collect_locations(target="test")
    assert len(results) == 1
    point = results[0]
    assert point.latitude == pytest.approx(37.4848)
    assert point.longitude == pytest.approx(-122.1484)
    assert point.source == "https://www.facebook.com"
    assert "Meta" in point.context
