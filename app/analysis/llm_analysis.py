from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence

import networkx as nx
import requests

from .data_loader import LocationRecord

logger = logging.getLogger(__name__)


SUPPORTED_LOCAL_LLM_MODELS: List[Dict[str, object]] = [
    {
        "name": "llama3.2:latest",
        "size_gb": 2.0,
        "description": "Meta Llama 3.2 distilled for laptops; balanced reasoning and speed on Apple Silicon.",
    },
    {
        "name": "phi4-mini:latest",
        "size_gb": 2.5,
        "description": "Microsoft Phi-4 mini tuned for assistant style tasks with low VRAM requirements.",
    },
    {
        "name": "wizardlm2:7b",
        "size_gb": 4.1,
        "description": "WizardLM 2 7B instruction model delivering strong investigative synthesis on consumer GPUs/NPUs.",
    },
]


DEFAULT_PROMPT_TEMPLATE = (
    "You are an investigative assistant for CreepyAI-25. Analyse the provided"
    " geospatial activity for {subject} with an {tone} tone and a {depth} level"
    " of detail. Prioritise the focus, if supplied: {focus}. Use the summary"
    " insights and record excerpts to build actionable findings that directly"
    " support locating the subject.\n\nSummary context:\n{summary}\n\n"
    "Records excerpt:\n{records}\n\nReturn a JSON object with keys"
    " 'key_connections', 'priority_locations', and 'next_steps'. Each key"
    " should map to a list of objects describing actionable insights with"
    " confidence or rationale fields."
)


@dataclass
class OllamaResponse:
    """Container for responses from the local Ollama API."""

    model: str
    prompt: str
    response: str
    created_at: datetime


class OllamaClient:
    """Thin wrapper around the local Ollama HTTP API used by CreepyAI-25."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434",
        session: Optional[requests.Session] = None,
        timeout: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        options: Optional[Mapping[str, object]] = None,
    ) -> OllamaResponse:
        payload: Dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if options:
            payload["options"] = dict(options)

        response = self.session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        text = data.get("response")
        if not isinstance(text, str):
            raise RuntimeError(f"Unexpected Ollama response: {data!r}")

        created = data.get("created_at")
        created_at = _parse_created_at(created)
        return OllamaResponse(model=model, prompt=prompt, response=text, created_at=created_at)


class LocalLLMAnalyzer:
    """Coordinate local LLM runs to build investigative connections."""

    def __init__(
        self,
        *,
        models: Optional[Sequence[str]] = None,
        client: Optional[OllamaClient] = None,
        temperature: float = 0.2,
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
        default_tone: str = "objective",
        default_depth: str = "balanced",
        model_settings: Optional[Mapping[str, Mapping[str, object]]] = None,
        max_records: int = 75,
    ) -> None:
        if models is None:
            models = [entry["name"] for entry in SUPPORTED_LOCAL_LLM_MODELS]
        self.models = list(models)
        self.client = client or OllamaClient()
        self.temperature = temperature
        self.prompt_template = prompt_template
        self.default_tone = default_tone
        self.default_depth = default_depth
        self.model_settings: Dict[str, Mapping[str, object]] = (
            dict(model_settings) if model_settings else {}
        )
        self.max_records = max_records

    def analyze_subject(
        self,
        subject: str,
        records: Sequence[LocationRecord],
        *,
        focus: Optional[str] = None,
    ) -> Dict[str, object]:
        if not records:
            raise ValueError("No records supplied for analysis")

        record_list = list(records)
        trimmed_records = record_list[: self.max_records]
        prompt_payload = [record.to_prompt_dict() for record in trimmed_records]
        summary = _summarise_records(trimmed_records)
        graph = build_relationship_graph(subject, trimmed_records)
        graph_snapshot = _summarise_graph(graph)
        generated_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        model_results: List[Dict[str, object]] = []
        for model in self.models:
            settings = dict(self.model_settings.get(model, {}))
            tone = str(settings.get("tone", self.default_tone))
            depth = str(settings.get("depth", self.default_depth))
            model_prompt_template = str(
                settings.get("prompt_template", self.prompt_template)
            )
            prompt = _build_prompt(
                subject,
                prompt_payload,
                summary,
                focus=focus,
                tone=tone,
                depth=depth,
                template=model_prompt_template,
            )
            options = dict(settings.get("options", {}))
            temperature = float(settings.get("temperature", self.temperature))
            options.setdefault("temperature", temperature)
            try:
                response = self.client.generate(
                    model=model,
                    prompt=prompt,
                    options=options,
                )
            except Exception as exc:  # pragma: no cover - defensive path
                logger.error("Failed to execute model %s: %s", model, exc)
                model_results.append(
                    {
                        "model": model,
                        "error": str(exc),
                        "parsed": None,
                        "raw_response": None,
                        "prompt": prompt,
                        "options": options,
                        "tone": tone,
                        "depth": depth,
                    }
                )
                continue

            parsed = _parse_model_response(response.response)
            model_results.append(
                {
                    "model": model,
                    "response": response.response,
                    "parsed": parsed,
                    "started_at": response.created_at.isoformat(),
                    "prompt": prompt,
                    "options": options,
                    "tone": tone,
                    "depth": depth,
                    "template": model_prompt_template,
                }
            )

        return {
            "subject": subject,
            "focus": focus,
            "models": self.models,
            "records_analyzed": len(trimmed_records),
            "model_outputs": model_results,
            "record_summary": summary,
            "graph": graph_snapshot,
            "recommended_models": SUPPORTED_LOCAL_LLM_MODELS,
            "generated_at": generated_at.isoformat(),
            "prompt_template": self.prompt_template,
            "default_settings": {
                "temperature": self.temperature,
                "tone": self.default_tone,
                "depth": self.default_depth,
                "max_records": self.max_records,
            },
        }


def build_relationship_graph(subject: str, records: Sequence[LocationRecord]) -> nx.Graph:
    graph = nx.Graph()
    graph.graph["subject"] = subject
    graph.graph["generated_at"] = datetime.utcnow().isoformat()
    graph.add_node(subject, type="subject", label=subject)

    for record in records:
        location_node = _location_node_id(record)
        graph.add_node(
            location_node,
            type="location",
            label=record.display_name or record.name or location_node,
            latitude=record.latitude,
            longitude=record.longitude,
            source=record.source,
            slug=record.slug,
            collected_at=record.collected_at.isoformat(),
        )

        plugin_node = f"plugin::{record.slug}"
        if not graph.has_node(plugin_node):
            graph.add_node(
                plugin_node,
                type="plugin",
                label=record.plugin,
                slug=record.slug,
            )

        graph.add_edge(subject, location_node, relationship="linked", plugin=record.slug)
        graph.add_edge(plugin_node, location_node, relationship="reported", dataset=str(record.dataset_path))

    return graph


def _location_node_id(record: LocationRecord) -> str:
    return f"loc::{record.latitude:.5f}:{record.longitude:.5f}:{record.source_id}"


def _summarise_records(records: Sequence[LocationRecord]) -> Dict[str, object]:
    by_plugin: MutableMapping[str, Dict[str, object]] = {}
    categories: MutableMapping[str, int] = {}

    for record in records:
        plugin_summary = by_plugin.setdefault(
            record.slug,
            {
                "plugin": record.plugin,
                "slug": record.slug,
                "count": 0,
                "latest": datetime.min,
            },
        )
        plugin_summary["count"] = plugin_summary.get("count", 0) + 1
        normalised = _normalise_datetime(record.collected_at)
        plugin_summary["latest"] = max(
            _normalise_datetime(plugin_summary.get("latest", datetime.min)),
            normalised,
        )

        if record.category:
            categories[record.category] = categories.get(record.category, 0) + 1

    plugin_entries = [
        {
            "slug": slug,
            "plugin": details["plugin"],
            "count": details["count"],
            "latest": (
                _normalise_datetime(details.get("latest", datetime.min)).isoformat()
            ),
        }
        for slug, details in by_plugin.items()
    ]
    plugin_entries.sort(key=lambda entry: entry["count"], reverse=True)

    top_categories = sorted(categories.items(), key=lambda item: item[1], reverse=True)[:5]

    return {
        "total_records": len(records),
        "plugins": plugin_entries,
        "top_categories": [
            {"category": name, "count": count} for name, count in top_categories
        ],
    }


def _summarise_graph(graph: nx.Graph) -> Dict[str, object]:
    location_nodes = [
        (node, data)
        for node, data in graph.nodes(data=True)
        if data.get("type") == "location"
    ]

    ranked = sorted(
        location_nodes,
        key=lambda item: graph.degree(item[0]),
        reverse=True,
    )

    hotspots = [
        {
            "id": node,
            "label": data.get("label"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "degree": graph.degree(node),
            "slug": data.get("slug"),
        }
        for node, data in ranked[:5]
    ]

    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "hotspots": hotspots,
    }


def _build_prompt(
    subject: str,
    records: List[Dict[str, object]],
    summary: Dict[str, object],
    *,
    focus: Optional[str] = None,
    tone: str = "objective",
    depth: str = "balanced",
    template: str = DEFAULT_PROMPT_TEMPLATE,
) -> str:
    summary_json = json.dumps(summary, indent=2)
    records_json = json.dumps(records, indent=2)
    payload = {
        "subject": subject,
        "focus": focus,
        "summary": summary,
        "records": records,
        "instructions": template.format(
            subject=subject,
            focus=focus or "not specified",
            summary=summary_json,
            records=records_json,
            tone=tone,
            depth=depth,
        ),
    }
    return json.dumps(payload, indent=2)


def _parse_model_response(response: str) -> Optional[Mapping[str, object]]:
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return None

    if isinstance(parsed, Mapping):
        return parsed
    return None


def _parse_created_at(value: Optional[str]) -> datetime:
    if isinstance(value, str):
        normalised = value.replace("Z", "+00:00") if value.endswith("Z") else value
        try:
            return datetime.fromisoformat(normalised)
        except ValueError:
            logger.debug("Unable to parse Ollama timestamp %s", value)
    return datetime.utcnow()


def _normalise_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    return datetime.min


__all__ = [
    "SUPPORTED_LOCAL_LLM_MODELS",
    "OllamaClient",
    "LocalLLMAnalyzer",
    "build_relationship_graph",
    "DEFAULT_PROMPT_TEMPLATE",
]
