#!/usr/bin/env python3
"""Run local LLM analysis across CreepyAI-25 datasets."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from app.analysis import (
    LocalLLMAnalyzer,
    SUPPORTED_LOCAL_LLM_MODELS,
    load_social_media_records,
)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate CreepyAI-25 intelligence insights using local Ollama models.",
    )
    parser.add_argument("subject", help="Subject name or identifier for the investigation context.")
    parser.add_argument(
        "--focus",
        help="Optional focus area passed to the LLM (for example, 'recent sightings' or 'cross-platform overlap').",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=75,
        help="Maximum number of records to include in the prompt (default: 75).",
    )
    parser.add_argument(
        "--output",
        choices=["json", "pretty"],
        default="pretty",
        help="Output format for the analysis payload.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        help="Optional explicit list of Ollama model tags to run (defaults to recommended set).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    records = load_social_media_records(limit_per_plugin=args.limit)
    if not records:
        print("No curated datasets were found. Run scripts/collect_social_media_data.py first.", file=sys.stderr)
        return 1

    analyzer = LocalLLMAnalyzer(models=args.models or None, max_records=args.limit)
    result = analyzer.analyze_subject(args.subject, records, focus=args.focus)

    if args.output == "json":
        json.dump(result, sys.stdout, indent=2)
        print()
        return 0

    _print_pretty(result)
    return 0


def _print_pretty(payload: dict) -> None:
    print(f"Subject: {payload['subject']}")
    if payload.get("focus"):
        print(f"Focus: {payload['focus']}")
    print(f"Records analysed: {payload['records_analyzed']}")
    print("Models executed:")
    for entry in payload.get("model_outputs", []):
        status = "ok" if entry.get("parsed") is not None else "raw"
        if entry.get("error"):
            status = f"error: {entry['error']}"
        print(f"  - {entry.get('model')}: {status}")

    summary = payload.get("record_summary", {})
    if summary:
        print("\nPlugin coverage:")
        for plugin in summary.get("plugins", []):
            latest = plugin.get("latest") or "unknown"
            print(f"  - {plugin['plugin']} ({plugin['slug']}): {plugin['count']} records, latest {latest}")

        categories = summary.get("top_categories", [])
        if categories:
            print("\nTop categories:")
            for item in categories:
                print(f"  - {item['category']}: {item['count']} mentions")

    graph = payload.get("graph", {})
    if graph:
        print("\nGraph snapshot:")
        print(f"  Nodes: {graph.get('node_count')} | Edges: {graph.get('edge_count')}")
        hotspots = graph.get("hotspots", [])
        if hotspots:
            print("  Hotspots:")
            for hotspot in hotspots:
                label = hotspot.get("label") or hotspot.get("id")
                print(
                    f"    - {label} (slug={hotspot.get('slug')}, degree={hotspot.get('degree')}, "
                    f"lat={hotspot.get('latitude')}, lon={hotspot.get('longitude')})"
                )

    print("\nRecommended local Ollama models:")
    for model in SUPPORTED_LOCAL_LLM_MODELS:
        print(f"  - {model['name']} (~{model['size_gb']} GB): {model['description']}")

    print("\nModel outputs (raw excerpts):")
    for entry in payload.get("model_outputs", []):
        if entry.get("response"):
            print(f"\n[{entry['model']}]\n{entry['response'][:1000]}")
        elif entry.get("error"):
            print(f"\n[{entry['model']}] ERROR: {entry['error']}")


if __name__ == "__main__":
    sys.exit(main())
