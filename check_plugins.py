#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility script to check and troubleshoot the plugin system."""

from __future__ import annotations

import argparse
import logging
import sys
import traceback
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _extend_sys_path(base_dir: Path) -> None:
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))


def check_plugin_system(base_dir: Path) -> None:
    """Check if the plugin system is properly configured"""
    try:
        _extend_sys_path(base_dir)
        from app.core.plugins import PluginManager

        # Create plugin manager
        plugin_manager = PluginManager()
        
        # Discover plugins
        plugins = plugin_manager.discover_plugins()
        
        # Print summary
        print(f"\nDiscovered {len(plugins)} plugins")
        
        # Get plugins by category
        categories = plugin_manager.get_categories()
        
        for category in sorted(set(categories.values())):
            category_plugins = plugin_manager.get_plugins_by_category(category)
            print(f"\nCategory: {category.upper()} ({len(category_plugins)} plugins)")
            
            for name, plugin in sorted(category_plugins.items()):
                info = plugin.get_info() if hasattr(plugin, 'get_info') else {'name': name}
                print(f"  - {info.get('name', name)} (v{info.get('version', 'unknown')})")
        
        print("\nPlugin system check completed successfully.")
        
    except ImportError as e:
        logger.error("Failed to import plugin system: %s", e)
        logger.error("Make sure the app module is in the Python path.")
    except Exception as e:
        logger.error(f"Error checking plugin system: {e}")
        logger.error(traceback.format_exc())

def check_specific_plugin(plugin_name: str, base_dir: Path) -> None:
    """Check a specific plugin by name"""
    try:
        _extend_sys_path(base_dir)
        from app.core.plugins import PluginManager
        
        # Create plugin manager
        plugin_manager = PluginManager()
        
        # Discover plugins
        plugin_manager.discover_plugins()
        
        # Try to get the specific plugin
        plugin = plugin_manager.get_plugin(plugin_name)
        
        if not plugin:
            print(f"Plugin '{plugin_name}' not found.")
            
            # List available plugins
            print("\nAvailable plugins:")
            for name in sorted(plugin_manager.plugins.keys()):
                print(f"  - {name}")
                
            return
        
        # Print plugin details
        print(f"\nPlugin: {plugin_name}")
        
        # Get information
        if hasattr(plugin, 'get_info'):
            info = plugin.get_info()
            print(f"Name: {info.get('name', 'Unknown')}")
            print(f"Description: {info.get('description', 'No description')}")
            print(f"Version: {info.get('version', 'Unknown')}")
            print(f"Author: {info.get('author', 'Unknown')}")
        
        # Check for essential methods
        print("\nMethods:")
        for method_name in ['run', 'configure', 'get_info']:
            if hasattr(plugin, method_name) and callable(getattr(plugin, method_name)):
                print(f"  - {method_name}: Available")
            else:
                print(f"  - {method_name}: Missing")
        
        # Check configuration if available
        if hasattr(plugin, 'is_configured'):
            try:
                configured, message = plugin.is_configured()
                print(f"\nConfiguration status: {'Configured' if configured else 'Not configured'}")
                print(f"Configuration message: {message}")
            except Exception as e:
                print(f"\nError checking configuration: {e}")
        
        print("\nPlugin check completed.")
        
    except ImportError as e:
        logger.error("Failed to import plugin system: %s", e)
    except Exception as e:
        logger.error(f"Error checking plugin: {e}")
        logger.error(traceback.format_exc())

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect CreepyAI plugin registrations")
    parser.add_argument("--plugin", help="Specific plugin to inspect")
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parent, help="Project base directory")
    parser.add_argument("--verbose", action='store_true', help="Enable debug logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    base_dir = args.base_dir.resolve()
    if args.plugin:
        check_specific_plugin(args.plugin, base_dir)
    else:
        check_plugin_system(base_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
