#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Utilities for CreepyAI
Common utility functions for plugin development and management
"""

import os
import sys
import re
import json
import yaml
import logging
import hashlib
import tempfile
import shutil
import zipfile
import tarfile
from typing import Dict, List, Any, Optional, Tuple, Union, Iterator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("plugin_utils")

class TemporaryDirectory:
    """Context manager for temporary directories with better error handling"""
    
    def __init__(self, suffix=None, prefix=None, dir=None, keep=False):
        """Initialize with the same parameters as tempfile.mkdtemp"""
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.keep = keep
        self.path = None
        
    def __enter__(self):
        """Create the temporary directory"""
        self.path = tempfile.mkdtemp(suffix=self.suffix, prefix=self.prefix, dir=self.dir)
        return self.path
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the temporary directory unless keep=True"""
        if not self.keep and self.path and os.path.exists(self.path):
            shutil.rmtree(self.path, ignore_errors=True)

def extract_archive(archive_path: str, extract_to: Optional[str] = None) -> Optional[str]:
    """
    Extract ZIP or TAR archive to specified directory or to a temporary directory
    
    Args:
        archive_path: Path to the archive file
        extract_to: Directory to extract to (if None, uses a temporary directory)
        
    Returns:
        Path to the directory where the archive was extracted, or None if failed
    """
    try:
        # Determine archive type
        if not os.path.exists(archive_path):
            logger.error(f"Archive file not found: {archive_path}")
            return None
            
        # Create extraction directory if not provided
        if not extract_to:
            extract_to = tempfile.mkdtemp(prefix="creepyai_extract_")
        else:
            os.makedirs(extract_to, exist_ok=True)
        
        # Extract based on file type
        if archive_path.endswith(('.zip', '.ZIP')):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.endswith(('.tar.gz', '.tgz')):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_to)
        elif archive_path.endswith(('.tar')):
            with tarfile.open(archive_path, 'r') as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            logger.error(f"Unsupported archive format: {archive_path}")
            if not extract_to:
                shutil.rmtree(extract_to, ignore_errors=True)
            return None
            
        return extract_to
        
    except Exception as e:
        logger.error(f"Error extracting archive {archive_path}: {e}")
        if not extract_to:
            shutil.rmtree(extract_to, ignore_errors=True)
        return None

def find_files(directory: str, pattern: str) -> List[str]:
    """
    Find files in a directory matching a regex pattern
    
    Args:
        directory: Directory to search in
        pattern: Regular expression pattern to match filenames
        
    Returns:
        List of paths to matching files
    """
    result = []
    try:
        regex = re.compile(pattern)
        for root, _, files in os.walk(directory):
            for file in files:
                if regex.search(file):
                    result.append(os.path.join(root, file))
    except Exception as e:
        logger.error(f"Error finding files in {directory} with pattern {pattern}: {e}")
    
    return result

def compute_file_hash(file_path: str, hash_type: str = 'sha256') -> Optional[str]:
    """
    Compute hash for a file
    
    Args:
        file_path: Path to the file
        hash_type: Type of hash function to use (md5, sha1, sha256, etc.)
        
    Returns:
        Hash string or None if error
    """
    try:
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.warning(f"File not found or not a file: {file_path}")
            return None
            
        hash_func = getattr(hashlib, hash_type.lower())()
        
        with open(file_path, 'rb') as f:
            # Read and update hash in chunks for large files
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
                
        return hash_func.hexdigest()
        
    except Exception as e:
        logger.error(f"Error computing {hash_type} hash for {file_path}: {e}")
        return None

def detect_file_type(file_path: str) -> Optional[str]:
    """
    Detect the MIME type of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string or None if error
    """
    try:
        import magic
        return magic.from_file(file_path, mime=True)
    except ImportError:
        logger.warning("python-magic not installed. Using fallback file type detection.")
        # Fallback to basic extension-based detection
        ext_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.zip': 'application/zip',
            '.tar.gz': 'application/gzip',
            '.tgz': 'application/gzip',
        }
        
        _, ext = os.path.splitext(file_path.lower())
        return ext_mapping.get(ext, 'application/octet-stream')
    except Exception as e:
        logger.error(f"Error detecting file type for {file_path}: {e}")
        return None

def update_plugin(plugin_name: str, source: str) -> bool:
    """
    Update a plugin from source (file or URL)
    
    Args:
        plugin_name: Name of the plugin to update
        source: Source file path or URL
        
    Returns:
        True if update was successful, False otherwise
    """
    import requests
    
    try:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plugins_dir = os.path.join(project_dir, "plugins")
        plugin_file = os.path.join(plugins_dir, f"{plugin_name}.py")
        
        # Check if plugin exists
        if not os.path.exists(plugin_file):
            logger.error(f"Plugin {plugin_name} not found")
            return False
        
        # Create backup of existing plugin
        backup_file = f"{plugin_file}.bak"
        shutil.copy2(plugin_file, backup_file)
        logger.info(f"Created backup of {plugin_file}")
        
        # Download from URL or copy from file
        if source.startswith(('http://', 'https://')):
            response = requests.get(source)
            response.raise_for_status()
            content = response.text
            
            with open(plugin_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Updated {plugin_name} from URL: {source}")
            
        else:
            # Assume it's a local file
            if not os.path.exists(source):
                logger.error(f"Source file not found: {source}")
                # Restore backup
                shutil.move(backup_file, plugin_file)
                return False
                
            shutil.copy2(source, plugin_file)
            logger.info(f"Updated {plugin_name} from file: {source}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating plugin {plugin_name}: {e}")
        # Try to restore backup if it exists
        if 'backup_file' in locals() and os.path.exists(backup_file):
            shutil.move(backup_file, plugin_file)
            logger.info(f"Restored backup of {plugin_file} after failed update")
        return False

def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a configuration dictionary against a schema
    
    Args:
        config: Configuration dictionary to validate
        schema: Schema dictionary describing expected structure
        
    Returns:
        (is_valid, error_messages) tuple
    """
    errors = []
    
    try:
        # Check required fields
        if 'required' in schema:
            for field in schema['required']:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
        
        # Validate field types and values
        if 'properties' in schema:
            for field_name, field_schema in schema['properties'].items():
                if field_name in config:
                    field_value = config[field_name]
                    
                    # Check type
                    if 'type' in field_schema:
                        expected_type = field_schema['type']
                        if expected_type == 'string' and not isinstance(field_value, str):
                            errors.append(f"Field {field_name} must be a string")
                        elif expected_type == 'number' and not isinstance(field_value, (int, float)):
                            errors.append(f"Field {field_name} must be a number")
                        elif expected_type == 'integer' and not isinstance(field_value, int):
                            errors.append(f"Field {field_name} must be an integer")
                        elif expected_type == 'boolean' and not isinstance(field_value, bool):
                            errors.append(f"Field {field_name} must be a boolean")
                        elif expected_type == 'array' and not isinstance(field_value, list):
                            errors.append(f"Field {field_name} must be an array")
                        elif expected_type == 'object' and not isinstance(field_value, dict):
                            errors.append(f"Field {field_name} must be an object")
                    
                    # Check enum values
                    if 'enum' in field_schema and field_value not in field_schema['enum']:
                        errors.append(f"Field {field_name} must be one of: {', '.join(str(v) for v in field_schema['enum'])}")
                    
                    # Check min/max values
                    if 'minimum' in field_schema and isinstance(field_value, (int, float)):
                        if field_value < field_schema['minimum']:
                            errors.append(f"Field {field_name} must be >= {field_schema['minimum']}")
                    
                    if 'maximum' in field_schema and isinstance(field_value, (int, float)):
                        if field_value > field_schema['maximum']:
                            errors.append(f"Field {field_name} must be <= {field_schema['maximum']}")
                    
                    # Check string patterns
                    if 'pattern' in field_schema and isinstance(field_value, str):
                        if not re.match(field_schema['pattern'], field_value):
                            errors.append(f"Field {field_name} does not match pattern: {field_schema['pattern']}")
                    
                    # Check array min/max items
                    if isinstance(field_value, list):
                        if 'minItems' in field_schema and len(field_value) < field_schema['minItems']:
                            errors.append(f"Field {field_name} must have at least {field_schema['minItems']} items")
                        if 'maxItems' in field_schema and len(field_value) > field_schema['maxItems']:
                            errors.append(f"Field {field_name} must have at most {field_schema['maxItems']} items")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"Error validating configuration: {e}")
        return False, errors

def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON or YAML file
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        if not os.path.exists(config_file):
            logger.error(f"Configuration file not found: {config_file}")
            return {}
            
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f) or {}
            elif config_file.endswith('.json'):
                return json.load(f)
            else:
                logger.error(f"Unsupported configuration file format: {config_file}")
                return {}
                
    except Exception as e:
        logger.error(f"Error loading configuration from {config_file}: {e}")
        return {}

def save_config(config: Dict[str, Any], config_file: str) -> bool:
    """
    Save configuration to a JSON or YAML file
    
    Args:
        config: Configuration dictionary
        config_file: Path to the configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.endswith(('.yaml', '.yml')):
                yaml.dump(config, f, default_flow_style=False)
            elif config_file.endswith('.json'):
                json.dump(config, f, indent=2)
            else:
                logger.error(f"Unsupported configuration file format: {config_file}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration to {config_file}: {e}")
        return False
