"""Simple command line interface for listing and running plugins."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.plugins.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


class PluginCLI:
    def __init__(self) -> None:
        self.manager = PluginManager()
        self.parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="CreepyAI Plugin CLI")
        subparsers = parser.add_subparsers(dest="command")

        list_parser = subparsers.add_parser("list", help="List available plugins")
        list_parser.add_argument("--verbose", action="store_true", help="Show plugin metadata")

        info_parser = subparsers.add_parser("info", help="Display information about a plugin")
        info_parser.add_argument("plugin", help="Plugin identifier")

        run_parser = subparsers.add_parser("run", help="Execute a plugin and print the result")
        run_parser.add_argument("plugin", help="Plugin identifier")
        run_parser.add_argument("target", nargs="?", default="", help="Target argument for the plugin")

        return parser

    # ------------------------------------------------------------------
    def run(self, argv: Optional[List[str]] = None) -> int:
        args = self.parser.parse_args(argv)
        if not getattr(args, "command", None):
            args = self.parser.parse_args(["list"])
        command = args.command

        if not getattr(self.manager, "plugins", {}):
            self.manager.initialize()

        handler = getattr(self, f"_handle_{command}")
        return handler(args)

    def _handle_list(self, args: argparse.Namespace) -> int:
        manifest = self.manager.get_manifest()
        for identifier, entry in sorted(manifest.items()):
            info = entry.get("info", {})
            if args.verbose:
                print(f"{identifier}: {json.dumps(info, indent=2)}")
            else:
                print(f"{identifier}: {info.get('name', identifier)}")
        return 0

    def _handle_info(self, args: argparse.Namespace) -> int:
        manifest = self.manager.get_manifest()
        info = manifest.get(args.plugin, {}).get("info")
        if not info:
            logger.error("Plugin %s not found", args.plugin)
            return 1
        print(json.dumps(info, indent=2))
        return 0

    def _handle_run(self, args: argparse.Namespace) -> int:
        plugin = self.manager.get_plugin(args.plugin)
        if not plugin:
            logger.error("Plugin %s not found", args.plugin)
            return 1
        result = plugin.run(args.target)
        if isinstance(result, list):
            serialised = [self._serialise_location(item) for item in result]
        else:
            serialised = result
        print(json.dumps(serialised, default=str, indent=2))
        return 0

    @staticmethod
    def _serialise_location(item: Any) -> Dict[str, Any]:
        if hasattr(item, "__dict__"):
            data = dict(item.__dict__)
            if isinstance(data.get("timestamp"), datetime):
                data["timestamp"] = data["timestamp"].isoformat()
            return data
        return {"value": str(item)}


def main(argv: Optional[List[str]] = None) -> int:
    cli = PluginCLI()
    return cli.run(argv)


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    raise SystemExit(main())
