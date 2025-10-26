#!/usr/bin/env python3
"""Script to inspect plugin-related directories and report their contents.

Enhancements over the previous version:

* Supports custom project roots via ``--base-dir``.
* Can emit a JSON summary (``--json``) for automation while still printing a
  readable human report.
* Adds structured error handling and exit codes.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PluginDirectoryInspector:
    """Inspects plugin-related directories and reports their contents"""
    
    def __init__(self, base_dir: Path):
        """Initialize with the project base directory"""
        self.base_dir = base_dir
        self.plugin_dirs = {
            'configs': base_dir / 'configs' / 'plugins',
            'templates': base_dir / 'resources' / 'templates' / 'plugins',
            'plugins': base_dir / 'app' / 'plugins',
        }
        
    def check_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Check a directory and return information about its contents"""
        result = {
            'exists': dir_path.exists(),
            'is_dir': dir_path.is_dir(),
            'files': [],
            'subdirs': [],
            'py_files': 0,
            'json_files': 0,
            'yaml_files': 0,
            'other_files': 0
        }
        
        if not result['exists'] or not result['is_dir']:
            return result

        for item in dir_path.iterdir():
            item_path = item

            if item_path.is_dir():
                result['subdirs'].append({
                    'name': item_path.name,
                    'path': str(item_path),
                    'item_count': sum(1 for _ in item_path.iterdir()),
                })
            else:
                file_info = {
                    'name': item_path.name,
                    'size': item_path.stat().st_size,
                    'type': self._get_file_type(item_path.name),
                }
                result['files'].append(file_info)

                # Count file types
                if item_path.name.endswith('.py'):
                    result['py_files'] += 1
                elif item_path.name.endswith('.json'):
                    result['json_files'] += 1
                elif item_path.name.endswith(('.yaml', '.yml')):
                    result['yaml_files'] += 1
                else:
                    result['other_files'] += 1
                    
        return result
        
    def _get_file_type(self, filename: str) -> str:
        """Get the type of a file based on its extension"""
        if filename.endswith('.py'):
            return 'Python'
        elif filename.endswith('.json'):
            return 'JSON'
        elif filename.endswith(('.yaml', '.yml')):
            return 'YAML'
        elif filename.endswith('.md'):
            return 'Markdown'
        elif filename.endswith('.txt'):
            return 'Text'
        elif filename.endswith(('.ini', '.cfg')):
            return 'Config'
        else:
            return 'Other'
            
    def check_all_directories(self) -> Dict[str, Dict[str, Any]]:
        """Check all plugin-related directories"""
        results = {}

        for name, dir_path in self.plugin_dirs.items():
            results[name] = self.check_directory(dir_path)

        return results
        
    def get_yaml_config_summary(self, filename: Path) -> Optional[Dict[str, Any]]:
        """Get a summary of a YAML config file"""
        try:
            with filename.open('r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            summary = {
                'keys': list(data.keys()) if isinstance(data, dict) else [],
                'structure': self._summarize_structure(data)
            }
            return summary
        except Exception as e:
            logger.error(f"Error reading YAML file {filename}: {e}")
            return None
            
    def get_json_config_summary(self, filename: Path) -> Optional[Dict[str, Any]]:
        """Get a summary of a JSON config file"""
        try:
            with filename.open('r', encoding='utf-8') as f:
                data = json.load(f)
                
            summary = {
                'keys': list(data.keys()) if isinstance(data, dict) else [],
                'structure': self._summarize_structure(data)
            }
            return summary
        except Exception as e:
            logger.error(f"Error reading JSON file {filename}: {e}")
            return None
    
    def _summarize_structure(self, data: Any, depth: int = 0) -> Any:
        """Recursively summarize the structure of data"""
        if depth > 2:  # Limit recursion depth
            return "..."
            
        if isinstance(data, dict):
            return {k: self._summarize_structure(v, depth + 1) for k, v in data.items()}
        elif isinstance(data, list):
            if not data:
                return []
            if len(data) > 3:
                return [self._summarize_structure(data[0], depth + 1), "..."]
            return [self._summarize_structure(item, depth + 1) for item in data]
        elif isinstance(data, (int, float, bool, str)):
            return type(data).__name__
        else:
            return str(type(data).__name__)
    
    def print_directory_report(self) -> None:
        """Print a report on all plugin directories"""
        results = self.check_all_directories()
        
        print("\n=== PLUGIN DIRECTORY INSPECTION REPORT ===\n")
        
        for name, result in results.items():
            full_path = self.plugin_dirs[name]
            exists = "EXISTS" if result['exists'] else "MISSING"
            
            print(f"\n== {name.upper()} DIRECTORY ({exists}) ==")
            print(f"Path: {full_path}")
            
            if not result['exists']:
                print("  Directory does not exist.")
                continue
                
            if not result['is_dir']:
                print("  Not a directory.")
                continue
                
            file_count = len(result['files'])
            subdir_count = len(result['subdirs'])
            
            print(f"Contents: {file_count} files, {subdir_count} subdirectories")
            print(f"File Types: {result['py_files']} Python, {result['json_files']} JSON, "
                 f"{result['yaml_files']} YAML, {result['other_files']} Other")
            
            if subdir_count > 0:
                print("\nSubdirectories:")
                for subdir in sorted(result['subdirs'], key=lambda d: d['name']):
                    print(f"  - {subdir['name']} ({subdir['item_count']} items)")
            
            if file_count > 0:
                print("\nFiles:")
                for file in sorted(result['files'], key=lambda f: f['name']):
                    size_kb = file['size'] / 1024
                    print(f"  - {file['name']} ({file['type']}, {size_kb:.1f} KB)")
                    
            # Additional processing for config files
            if name == 'configs':
                print("\nConfig File Summaries:")
                for file in result['files']:
                    if file['name'].endswith('.json'):
                        file_path = full_path / file['name']
                        summary = self.get_json_config_summary(file_path)
                        if summary:
                            print(f"  {file['name']} keys: {', '.join(summary['keys'])}")
                    elif file['name'].endswith(('.yaml', '.yml')):
                        file_path = full_path / file['name']
                        summary = self.get_yaml_config_summary(file_path)
                        if summary:
                            print(f"  {file['name']} keys: {', '.join(summary['keys'])}")
                            
            # Additional processing for template files
            if name == 'templates':
                print("\nTemplate File Information:")
                for file in result['files']:
                    if file['name'].endswith('.py'):
                        file_path = full_path / file['name']
                        try:
                            with file_path.open('r', encoding='utf-8') as f:
                                lines = f.readlines()
                                print(f"  {file['name']}: {len(lines)} lines")
                                # Try to extract template name/purpose
                                for line in lines[:20]:
                                    if '"""' in line or "'''" in line:
                                        doc = line.strip().strip('"\'')
                                        if doc:
                                            print(f"    {doc}")
                                            break
                        except Exception as e:
                            logger.error(f"Error reading template file {file_path}: {e}")
            
            # Additional processing for plugin files
            if name == 'plugins':
                plugin_categories = {}
                for subdir in result['subdirs']:
                    plugin_categories[subdir['name']] = []
                    subdir_path = full_path / subdir['name']
                    if subdir_path.exists() and subdir_path.is_dir():
                        for item in subdir_path.iterdir():
                            if item.suffix == '.py' and not item.name.startswith('__'):
                                plugin_categories[subdir['name']].append(item.name)
                                
                print("\nPlugin Categories:")
                for category, plugins in plugin_categories.items():
                    print(f"  {category} ({len(plugins)} plugins)")
                    if plugins:
                        for plugin in sorted(plugins):
                            print(f"    - {plugin}")
        
        print("\n=== END OF REPORT ===\n")

def dump_json_report(report: Dict[str, Dict[str, Any]], output: Optional[Path]) -> None:
    payload = json.dumps(report, indent=2, sort_keys=True)
    if output:
        output.write_text(payload, encoding='utf-8')
        logger.info("Wrote JSON report to %s", output)
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect CreepyAI plugin directories")
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parent, help="Project root directory")
    parser.add_argument("--json", type=Path, nargs="?", const=Path("-"), help="Emit JSON report to stdout or file")
    parser.add_argument("--summary-only", action="store_true", help="Skip the verbose console report")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_dir = args.base_dir.resolve()
    inspector = PluginDirectoryInspector(base_dir)
    report = inspector.check_all_directories()

    if args.json is not None:
        output = None if args.json == Path("-") else args.json.resolve()
        dump_json_report(report, output)

    if not args.summary_only:
        inspector.print_directory_report()

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
