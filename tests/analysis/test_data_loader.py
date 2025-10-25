import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_user_dirs(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path))
    return tmp_path


def test_load_social_media_records_reads_curated_dataset(isolate_user_dirs):
    from app.analysis.data_loader import load_social_media_records
    from app.plugins.social_media.facebook_plugin import FacebookPlugin

    plugin = FacebookPlugin()
    dataset_path = Path(plugin.get_data_directory()) / plugin.dataset_filename
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": {"updated_at": "2024-08-01T00:00:00+00:00"},
        "records": [
            {
                "source_id": "osm:123",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "name": "Test Location",
                "category": "landmark",
                "display_name": "Test Location, London",
                "source": "https://facebook.com",
                "collected_at": "2024-08-01T12:00:00+00:00",
                "raw": {"note": "sample"},
            }
        ],
    }
    dataset_path.write_text(json.dumps(payload), encoding="utf-8")

    records = load_social_media_records()
    assert len(records) == 1

    record = records[0]
    assert record.plugin == plugin.name
    assert record.slug == "facebook"
    assert record.source_id == "osm:123"
    assert record.latitude == pytest.approx(51.5074)
    assert record.longitude == pytest.approx(-0.1278)
    assert record.collected_at.year == 2024
    assert record.display_name == "Test Location, London"
