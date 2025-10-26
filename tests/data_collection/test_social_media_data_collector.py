from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence

import pytest

from app.data_collection.social_media_data_collector import SocialMediaDataCollector


@pytest.fixture()
def collector(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    captured_queries = {}

    def fake_fetcher(query: str) -> Sequence[Mapping[str, object]]:
        captured_queries.setdefault(query, 0)
        captured_queries[query] += 1
        return [
            {
                "osm_type": "node",
                "osm_id": 123,
                "lat": 37.4848,
                "lon": -122.1484,
                "name": f"{query} Campus",
                "display_name": f"{query} Campus",
                "type": "office",
            }
        ]

    collector = SocialMediaDataCollector(fetcher=fake_fetcher)
    return collector, captured_queries


def read_dataset(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_collector_writes_datasets(collector):
    collector_instance, captured_queries = collector
    results = collector_instance.collect()

    assert results
    for slug, dataset_path in results.items():
        data = read_dataset(dataset_path)
        assert dataset_path.name == "collected_locations.json"
        assert data["records"]
        for record in data["records"]:
            assert "latitude" in record
            assert "longitude" in record
            assert record["source_id"]
    # ensure fetcher invoked for configured terms
    assert captured_queries


def test_collector_deduplicates_existing_records(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))

    def fake_fetcher(query: str) -> Sequence[Mapping[str, object]]:
        return [
            {
                "osm_type": "node",
                "osm_id": 999,
                "lat": 40.0,
                "lon": -70.0,
                "name": "Existing Site",
                "display_name": "Existing Site",
                "type": "office",
            }
        ]

    collector = SocialMediaDataCollector(fetcher=fake_fetcher)
    results = collector.collect(["facebook"])
    dataset_path = results["facebook"]

    first_payload = read_dataset(dataset_path)
    first_timestamp = first_payload["records"][0]["collected_at"]

    # Create older dataset to ensure dedupe keeps the newest timestamp
    older_payload = {
        "metadata": {"updated_at": "2023-01-01T00:00:00+00:00"},
        "records": [
            {
                "source_id": "node:999",
                "latitude": 40.0,
                "longitude": -70.0,
                "name": "Existing Site",
                "category": "office",
                "display_name": "Existing Site",
                "source": "https://www.facebook.com",
                "collected_at": "2023-01-01T00:00:00+00:00",
            }
        ],
    }

    dataset_path.write_text(json.dumps(older_payload), encoding="utf-8")

    refreshed = collector.collect(["facebook"])
    refreshed_payload = read_dataset(refreshed["facebook"])

    assert len(refreshed_payload["records"]) == 1
    assert refreshed_payload["records"][0]["collected_at"] >= first_timestamp

