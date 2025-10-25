import json
from datetime import datetime, timezone

from app.analysis.history import load_recent_history, persist_analysis_result


def test_persist_analysis_result_writes_file_and_hash(tmp_path):
    payload = {
        "subject": "Test Subject",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records_analyzed": 3,
        "model_outputs": [],
    }

    entry = persist_analysis_result(tmp_path, payload)

    assert entry.file_path.exists()
    assert entry.integrity.startswith("sha256:")

    saved = json.loads(entry.file_path.read_text(encoding="utf-8"))
    assert saved["integrity"] == entry.integrity

    history = load_recent_history(tmp_path, limit=5)
    assert history
    assert history[0].integrity == entry.integrity


def test_load_recent_history_recalculates_integrity(tmp_path):
    path = tmp_path / "20240101T000000Z_test.json"
    payload = {
        "subject": "History Subject",
        "generated_at": "2024-01-01T00:00:00+00:00",
        "records_analyzed": 1,
        "model_outputs": [],
        "integrity": "sha256:invalid",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    entries = load_recent_history(tmp_path, limit=5)
    assert entries
    entry = entries[0]
    assert entry.integrity.startswith("sha256:")
    assert entry.integrity != "sha256:invalid"
