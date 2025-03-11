#!/usr/bin/env python3
"""
Script to inspect plugin-related directories and report their contents
"""
import os
import sys
import json
import yaml
import logging
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PluginDirectoryInspector:
    """Inspects plugin-related directories and reports their contents"""
    
    def __init__(self, base_dir: str):
        """Initialize with the project base directory"""
        self.base_dir = base_dir
        self.plugin_dirs = {
            'configs': os.path.join(base_dir, 'configs', 'plugins'),
            'templates': os.path.join(base_dir, 'resources', 'templates', 'plugins'),
            'plugins': os.path.join(base_dir, 'app', 'plugins')
        }
        
    def check_directory(self, dir_path: str) -> Dict[str, Any]:
        """Check a directory and return information about its contents"""
        result = {
            'exists': os.path.exists(dir_path),
            'is_dir': os.path.isdir(dir_path) if os.path.exists(dir_path) else False,
            'files': [],
            'subdirs': [],
            'py_files': 0,
            'json_files': 0,
            'yaml_files': 0,
            'other_files': 0
        }
        
        if not result['exists'] or not result['is_dir']:
            return result
            
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            
            if os.path.isdir(item_path):
                result['subdirs'].append({
                    'name': item,
                    'path': item_path,
                    'item_count': len(os.listdir(item_path))
                })
            else:
                file_info = {
                    'name': item,
                    'size': os.path.getsize(item_path),
                    'type': self._get_file_type(item)
                }
                result['files'].append(file_info)
                
                # Count file types
                if item.endswith('.py'):
                    result['py_files'] += 1
                elif item.endswith('.json'):
                    result['json_files'] += 1
                elif item.endswith(('.yaml', '.yml')):
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
        
    def get_yaml_config_summary(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a YAML config file"""
        try:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
                
            summary = {
                'keys': list(data.keys()) if isinstance(data, dict) else [],
                'structure': self._summarize_structure(data)
            }
            return summary
        except Exception as e:
            logger.error(f"Error reading YAML file {filename}: {e}")
            return None
            
    def get_json_config_summary(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a JSON config file"""
        try:
            with open(filename, 'r') as f:
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
                        file_path = os.path.join(full_path, file['name'])
                        summary = self.get_json_config_summary(file_path)
                        if summary:
                            print(f"  {file['name']} keys: {', '.join(summary['keys'])}")
                    elif file['name'].endswith(('.yaml', '.yml')):
                        file_path = os.path.join(full_path, file['name'])
                        summary = self.get_yaml_config_summary(file_path)
                        if summary:
                            print(f"  {file['name']} keys: {', '.join(summary['keys'])}")
                            
            # Additional processing for template files
            if name == 'templates':
                print("\nTemplate File Information:")
                for file in result['files']:
                    if file['name'].endswith('.py'):
                        file_path = os.path.join(full_path, file['name'])
                        try:
                            with open(file_path, 'r') as f:
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
                    subdir_path = os.path.join(full_path, subdir['name'])
                    if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
                        for item in os.listdir(subdir_path):
                            if item.endswith('.py') and not item.startswith('__'):
                                plugin_categories[subdir['name']].append(item)
                                
                print("\nPlugin Categories:")
                for category, plugins in plugin_categories.items():
                    print(f"  {category} ({len(plugins)} plugins)")
                    if plugins:
                        for plugin in sorted(plugins):
                            print(f"    - {plugin}")
        
        print("\n=== END OF REPORT ===\n")

def main():
    """Main function"""
    # Use the script directory as base, assuming script is in project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    inspector = PluginDirectoryInspector(base_dir)
    inspector.print_directory_report()

if __name__ == "__main__":
    main()
