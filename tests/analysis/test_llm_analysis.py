import json
from datetime import datetime, timezone
from pathlib import Path

from app.analysis.data_loader import LocationRecord
from app.analysis.llm_analysis import LocalLLMAnalyzer, OllamaResponse


class FakeClient:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls = []

    def generate(self, *, model: str, prompt: str, options=None):
        self.calls.append({"model": model, "prompt": prompt, "options": options})
        return OllamaResponse(
            model=model,
            prompt=prompt,
            response=self.response_text,
            created_at=datetime.now(timezone.utc),
        )


def test_local_llm_analyzer_parses_json_payload():
    record = LocationRecord(
        plugin="Facebook",
        slug="facebook",
        dataset_path=Path("/tmp/facebook.json"),
        source_id="osm:123",
        latitude=40.0,
        longitude=-75.0,
        name="Sample",
        category="park",
        display_name="Sample Park",
        collected_at=datetime.now(timezone.utc),
        source="https://facebook.com",
        raw={"note": "example"},
    )

    payload = {
        "key_connections": [
            {"summary": "Linked visit", "confidence": 0.7}
        ],
        "priority_locations": [
            {"name": "Sample Park", "reason": "Recent activity"}
        ],
        "next_steps": [
            {"action": "Verify onsite cameras"}
        ],
    }

    fake_client = FakeClient(response_text=json.dumps(payload))
    analyzer = LocalLLMAnalyzer(models=["llama3.2:latest"], client=fake_client, max_records=10)

    result = analyzer.analyze_subject("Alex Doe", [record])
    assert result["records_analyzed"] == 1
    assert result["model_outputs"][0]["parsed"] == payload
    assert "generated_at" in result
    assert result["prompt_template"]
    assert result["default_settings"]["tone"] == "objective"
    assert result["model_outputs"][0]["prompt"].startswith("{")

    call = fake_client.calls[0]
    assert call["model"] == "llama3.2:latest"
    assert call["options"]["temperature"] == analyzer.temperature

    graph = result["graph"]
    assert graph["node_count"] >= 3
    assert graph["hotspots"][0]["label"] == "Sample Park"


def test_local_llm_analyzer_respects_model_overrides():
    record = LocationRecord(
        plugin="Twitter",
        slug="twitter",
        dataset_path=Path("/tmp/twitter.json"),
        source_id="osm:999",
        latitude=41.0,
        longitude=-74.0,
        name="Another", 
        category="cafe",
        display_name="Another Cafe",
        collected_at=datetime.now(timezone.utc),
        source="https://twitter.com",
        raw={"note": "second"},
    )

    fake_client = FakeClient(response_text="{}")
    overrides = {
        "wizardlm2:7b": {
            "temperature": 0.75,
            "tone": "narrative",
            "depth": "comprehensive",
            "prompt_template": "Narrate findings about {subject} with tone={tone} depth={depth}.",
        }
    }

    analyzer = LocalLLMAnalyzer(
        models=["wizardlm2:7b"],
        client=fake_client,
        max_records=5,
        temperature=0.1,
        prompt_template="Default {tone} {depth}",
        default_tone="objective",
        default_depth="concise",
        model_settings=overrides,
    )

    result = analyzer.analyze_subject("Jamie Example", [record])

    call = fake_client.calls[0]
    assert call["options"]["temperature"] == 0.75
    assert "narrative" in call["prompt"]
    assert "comprehensive" in call["prompt"]

    output = result["model_outputs"][0]
    assert output["tone"] == "narrative"
    assert output["depth"] == "comprehensive"
    assert output["template"].startswith("Narrate findings")
