from __future__ import annotations

import importlib
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

    for cls in module.SOCIAL_MEDIA_PLUGINS.values():
        plugin = cls()
        data_dir = Path(plugin.get_data_directory())
        assert data_dir.is_dir()
        assert data_dir.parent == imports_root
        assert not any(data_dir.iterdir())
