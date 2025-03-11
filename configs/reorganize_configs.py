    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to reorganize configuration files in CreepyAI project.
This script moves configuration files to the config/ directory and updates references.
"""

import os
import re
import shutil
import sys
from pathlib import Path
import json
import yaml
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path('/Users/mbaosint/Desktop/Projects/CreepyAI')

# Target configuration directory
CONFIG_DIR = PROJECT_ROOT / 'config'

# Configuration subdirectories to create
CONFIG_SUBDIRS = [
    CONFIG_DIR / 'plugins',
    CONFIG_DIR / 'logging',
    CONFIG_DIR / 'app'
]

# Files to move (source_path, target_subdir)
FILES_TO_MOVE = [
    # For example:
    ('plugins/logging_config.json', 'logging'),
    ('plugins/plugins.yaml', 'plugins'),
    # Add more files here as they're identified
]

# Regex patterns to update file references in code
FILE_REFERENCE_PATTERNS = {
    r'["\']plugins/logging_config\.json["\']': '"config/logging/logging_config.json"',
    r'["\']plugins/plugins\.yaml["\']': '"config/plugins/plugins.yaml"',
    # Add more patterns as needed
}

def ensure_config_dirs():
    """Create the config directory structure if it doesn't exist"""
    for dir_path in CONFIG_SUBDIRS:
        dir_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created configuration directory structure in {CONFIG_DIR}")

def find_config_files():
    """Find potential configuration files in the project"""
    config_files = []
    
    # Extensions typically used for config files
    config_extensions = ['.json', '.yaml', '.yml', '.conf', '.cfg', '.ini', '.xml', '.toml']
    
    # Find files with config-like extensions
    for ext in config_extensions:
        for filepath in PROJECT_ROOT.glob(f'**/*{ext}'):
            # Skip files already in config/ directory
            if 'config/' in str(filepath) or '/config/' in str(filepath):
                continue
                
            # Skip files in certain directories
            if any(d in str(filepath) for d in ['/venv/', '/.git/', '/.idea/', '__pycache__']):
                continue
                
            # Check if file is likely a config file (either by name or content)
            filename = filepath.name.lower()
            if ('config' in filename or 
                'settings' in filename or 
                'preferences' in filename or 
                'options' in filename):
                config_files.append(filepath)
                continue
                
            # Simple heuristic: check first few lines for config-like content
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = ''.join(f.readline() for _ in range(5))
                    if ('{' in first_lines and ':' in first_lines) or ('=' in first_lines):
                        config_files.append(filepath)
            except:
                pass
    
    return config_files

def determine_config_type(filepath):
    """Determine which subtype a configuration file belongs to"""
    filename = filepath.name.lower()
    file_path_str = str(filepath).lower()
    
    # Check for plugin-related configs
    if 'plugin' in filename or 'plugin' in file_path_str:
        return 'plugins'
    
    # Check for logging-related configs
    if 'log' in filename or 'logging' in file_path_str:
        return 'logging'
    
    # Default to app config
    return 'app'

def move_config_file(source_path, config_type):
    """Move a config file to its appropriate directory"""
    source_path = Path(source_path)
    if not source_path.exists():
        logger.warning(f"Source file not found: {source_path}")
        return None
    
    target_dir = CONFIG_DIR / config_type
    target_path = target_dir / source_path.name
    
    # Create backup if target file already exists
    if target_path.exists():
        backup_path = target_path.with_suffix(f"{target_path.suffix}.bak")
        shutil.copy2(target_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
    
    # Copy the file to target directory
    shutil.copy2(source_path, target_path)
    logger.info(f"Moved {source_path} -> {target_path}")
    
    return target_path

def update_file_references(file_path, patterns):
    """Update references to moved configuration files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        
        # Apply replacement patterns
        for pattern, replacement in patterns.items():
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Updated file references in {file_path}")
    
    except Exception as e:
        logger.error(f"Error updating file {file_path}: {e}")

def create_config_module():
    """Update the config/__init__.py module to provide convenient access to configurations"""
    init_path = CONFIG_DIR / '__init__.py'
    
    content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Configuration module for CreepyAI.
Provides easy access to configuration files and settings.
\"\"\"

import os
import json
import yaml
import logging
from pathlib import Path
import importlib.util
import configparser
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

# Configuration directories
CONFIG_DIR = Path(__file__).parent
PLUGINS_CONFIG_DIR = CONFIG_DIR / 'plugins'
LOGGING_CONFIG_DIR = CONFIG_DIR / 'logging'
APP_CONFIG_DIR = CONFIG_DIR / 'app'

def get_config_file_path(filename: str, subdir: Optional[str] = None) -> Path:
    \"\"\"
    Get the full path to a configuration file.
    
    Args:
        filename: Name of the config file
        subdir: Optional subdirectory in the config directory
    
    Returns:
        Path object for the config file
    \"\"\"
    if subdir:
        return CONFIG_DIR / subdir / filename
    return CONFIG_DIR / filename

def load_json_config(filename: str, subdir: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Load a JSON configuration file.
    
    Args:
        filename: Name of the JSON config file
        subdir: Optional subdirectory in the config directory
    
    Returns:
        Dictionary with configuration data
    \"\"\"
    config_path = get_config_file_path(filename, subdir)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON config {config_path}: {e}")
        return {}

def load_yaml_config(filename: str, subdir: Optional[str] = None) -> Dict[str, Any]:
    \"\"\"
    Load a YAML configuration file.
    
    Args:
        filename: Name of the YAML config file
        subdir: Optional subdirectory in the config directory
    
    Returns:
        Dictionary with configuration data
    \"\"\"
    config_path = get_config_file_path(filename, subdir)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading YAML config {config_path}: {e}")
        return {}

def load_ini_config(filename: str, subdir: Optional[str] = None) -> configparser.ConfigParser:
    \"\"\"
    Load an INI configuration file.
    
    Args:
        filename: Name of the INI config file
        subdir: Optional subdirectory in the config directory
    
    Returns:
        ConfigParser object with loaded configuration
    \"\"\"
    config_path = get_config_file_path(filename, subdir)
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
    except Exception as e:
        logger.error(f"Error loading INI config {config_path}: {e}")
    return config

def load_config(filename: str, subdir: Optional[str] = None) -> Any:
    \"\"\"
    Load a configuration file based on its extension.
    
    Args:
        filename: Name of the config file
        subdir: Optional subdirectory in the config directory
    
    Returns:
        Loaded configuration (format depends on file type)
    \"\"\"
    if filename.endswith(('.yaml', '.yml')):
        return load_yaml_config(filename, subdir)
    elif filename.endswith('.json'):
        return load_json_config(filename, subdir)
    elif filename.endswith(('.ini', '.cfg', '.conf')):
        return load_ini_config(filename, subdir)
    else:
        logger.warning(f"Unknown config file type for {filename}")
        return None

# Common configuration getters
def get_logging_config():
    \"\"\"Get the logging configuration\"\"\"
    return load_json_config('logging_config.json', 'logging')

def get_plugins_config():
    \"\"\"Get the plugins configuration\"\"\"
    return load_yaml_config('plugins.yaml', 'plugins')

def get_app_config():
    \"\"\"Get the application configuration\"\"\"
    return load_json_config('app_config.json', 'app')
"""
    
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Created config module: {init_path}")

def main():
    """Main function for reorganizing configurations"""
    logger.info("Starting configuration reorganization...")
    
    # Ensure config directories exist
    ensure_config_dirs()
    
    # Find potential config files
    potential_configs = find_config_files()
    logger.info(f"Found {len(potential_configs)} potential configuration files")
    
    # Present discovered files for confirmation
    print("\nPotential configuration files to move:")
    for i, file_path in enumerate(potential_configs):
        config_type = determine_config_type(file_path)
        print(f"{i+1}. {file_path} -> config/{config_type}/")
    
    # Get user confirmation for which files to move
    selection = input("\nEnter file numbers to move (comma-separated), 'all' for all, or 'skip' to manually specify: ")
    
    files_to_process = []
    
    if selection.lower() == 'all':
        files_to_process = [(str(p), determine_config_type(p)) for p in potential_configs]
    elif selection.lower() == 'skip':
        # Manual file specification
        while True:
            source = input("\nEnter source path (relative to project root, or 'done' to finish): ")
            if source.lower() == 'done':
                break
                
            config_type = input("Enter config type (plugins, logging, app): ")
            if config_type not in ['plugins', 'logging', 'app']:
                print("Invalid config type. Using 'app' as default.")
                config_type = 'app'
                
            files_to_process.append((source, config_type))
    else:
        try:
            indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
            for idx in indices:
                if 0 <= idx < len(potential_configs):
                    file_path = potential_configs[idx]
                    config_type = determine_config_type(file_path)
                    files_to_process.append((str(file_path), config_type))
        except ValueError:
            logger.error("Invalid selection. No files will be moved.")
            return 1
    
    # Move selected files
    moved_files = []
    for source_path, config_type in files_to_process:
        target_path = move_config_file(source_path, config_type)
        if target_path:
            moved_files.append((source_path, str(target_path)))
    
    if not moved_files:
        logger.warning("No files were moved.")
        return 0
    
    # Update reference patterns based on moved files
    update_patterns = {}
    for source, target in moved_files:
        # Create regex pattern to match references to this file
        source_parts = Path(source).parts
        if len(source_parts) > 1:  # Only if source has directory structure
            source_pattern = r'["\']' + '/'.join(source_parts) + r'["\']'
            target_pattern = '"' + str(Path(target).relative_to(PROJECT_ROOT)) + '"'
            update_patterns[source_pattern] = target_pattern
    
    # Update file references
    logger.info("Updating file references...")
    for py_file in PROJECT_ROOT.glob('**/*.py'):
        # Skip files in certain directories
        if any(d in str(py_file) for d in ['/venv/', '/.git/', '/.idea/', '__pycache__']):
            continue
            
        update_file_references(py_file, update_patterns)
    
    # Create config module
    create_config_module()
    
    # Summary
    logger.info("\nConfiguration reorganization completed!")
    logger.info(f"Moved {len(moved_files)} configuration files to {CONFIG_DIR}")
    
    print("\nNext steps:")
    print("1. Review the updated code to ensure file references were correctly updated")
    print("2. Delete the original configuration files if they are no longer needed")
    print("3. Update import statements in your code to use the new config module")
    print("   For example: from config import get_logging_config, get_plugins_config")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
