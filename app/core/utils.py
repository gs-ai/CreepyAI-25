"""
Common utility functions for CreepyAI
"""
import os
import sys
import json
import platform
import datetime
import time
import logging
import hashlib
import functools
import tempfile
import traceback
from typing import Dict, Any, List, Optional, Callable, TypeVar, Union, Tuple
from pathlib import Path

# Import path utilities
from .path_utils import (
    get_app_root, 
    get_user_data_dir,
    get_user_config_dir, 
    get_user_log_dir,
    get_dir, 
    normalize_path,
    find_file,
    ensure_app_dirs
)

logger = logging.getLogger('creepyai.core.utils')

# Type variable for generic functions
T = TypeVar('T')

def memoize(func: Callable) -> Callable:
    """Memoization decorator for optimizing repeated function calls"""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hash from the function arguments
        key_parts = [repr(arg) for arg in args]
        key_parts.extend(f"{k}={v!r}" for k, v in sorted(kwargs.items()))
        key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    # Add ability to clear the cache
    wrapper.clear_cache = cache.clear
    return wrapper

def timed(func: Callable) -> Callable:
    """Decorator for timing function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logging.debug(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper

def safe_execute(func: Callable[..., T], *args, **kwargs) -> Tuple[bool, Optional[T], Optional[Exception]]:
    """
    Safely execute a function and return its result along with success status.
    
    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Tuple of (success, result, exception)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}")
        logger.debug(traceback.format_exc())
        return False, None, e

def get_temp_dir() -> str:
    """Get a secure temporary directory with proper error handling"""
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), 'creepyai')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    except Exception as e:
        logging.error(f"Error creating temp directory: {e}")
        return tempfile.gettempdir()

def get_system_info() -> Dict[str, str]:
    """Get detailed system information"""
    info = {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'hostname': platform.node(),
        'architecture': platform.architecture()[0],
        'machine': platform.machine()
    }
    
    # Add memory information if available
    try:
        import psutil
        vm = psutil.virtual_memory()
        info['total_memory'] = f"{vm.total / (1024**3):.2f} GB"
        info['available_memory'] = f"{vm.available / (1024**3):.2f} GB"
    except ImportError:
        pass
        
    return info

def batch_process(items: List[T], func: Callable[[T], Any], batch_size: int = 100) -> List[Any]:
    """Process a large list in batches for better memory efficiency"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [func(item) for item in batch]
        results.extend(batch_results)
    return results

def json_to_file(data: Dict[str, Any], filepath: str) -> bool:
    """Save JSON data to file.
    
    Args:
        data: Data to save
        filepath: File path to save to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON to file {filepath}: {e}")
        return False

def file_to_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Load JSON data from file.
    
    Args:
        filepath: File path to load from
        
    Returns:
        Loaded JSON data or None if error
    """
    try:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON from file {filepath}: {e}")
        return None

def get_resource_paths() -> Dict[str, List[str]]:
    """Get standardized resource paths for the application.
    
    Returns:
        Dictionary mapping resource types to lists of directories
    """
    app_root = get_app_root()
    
    return {
        'images': [
            os.path.join(app_root, 'resources', 'assets', 'images'),
            os.path.join(app_root, 'resources', 'images'),
            os.path.join(app_root, 'assets', 'images'),
        ],
        'icons': [
            os.path.join(app_root, 'resources', 'assets', 'icons'),
            os.path.join(app_root, 'resources', 'icons'),
            os.path.join(app_root, 'assets', 'icons'),
            os.path.join(app_root, 'assets', 'icons', 'ui'),
        ],
        'html': [
            os.path.join(app_root, 'include'),
            os.path.join(app_root, 'resources', 'html'),
            os.path.join(app_root, 'src', 'include'),
        ],
        'templates': [
            os.path.join(app_root, 'resources', 'templates'),
            os.path.join(app_root, 'templates'),
        ],
        'plugins': [
            os.path.join(app_root, 'plugins', 'src'),
            os.path.join(app_root, 'plugins'),
        ],
        'configs': [
            os.path.join(app_root, 'configs'),
            os.path.join(app_root, 'config'),
            os.path.join(app_root, 'plugins', 'configs'),
        ],
    }

def format_timestamp(timestamp: Optional[datetime.datetime] = None, 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a timestamp as a string.
    
    Args:
        timestamp: Datetime to format (uses current time if None)
        format_str: Format string for strftime
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()
    return timestamp.strftime(format_str)

def create_directories(dir_paths: List[str]) -> Dict[str, bool]:
    """Create multiple directories and report success.
    
    Args:
        dir_paths: List of directory paths to create
        
    Returns:
        Dictionary mapping paths to success status
    """
    results = {}
    for path in dir_paths:
        try:
            os.makedirs(path, exist_ok=True)
            results[path] = True
        except Exception as e:
            logging.error(f"Error creating directory {path}: {e}")
            results[path] = False
    return results

def yaml_to_dict(yaml_str: str) -> Dict[str, Any]:
    """Convert YAML string to dictionary.
    
    Args:
        yaml_str: YAML string
        
    Returns:
        Dictionary parsed from YAML
    """
    try:
        import yaml
        return yaml.safe_load(yaml_str) or {}
    except Exception as e:
        logging.error(f"Error parsing YAML: {e}")
        return {}

def dict_to_yaml(data: Dict[str, Any]) -> str:
    """Convert dictionary to YAML string.
    
    Args:
        data: Dictionary to convert
        
    Returns:
        YAML string representation
    """
    try:
        import yaml
        return yaml.safe_dump(data, default_flow_style=False)
    except Exception as e:
        logging.error(f"Error converting to YAML: {e}")
        return ""

def load_json_file(file_path: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Load a JSON file safely.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Tuple of (success, data)
    """
    import json
    
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False, None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return False, None

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
        
    Returns:
        True if successful, False otherwise
    """
    import json
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False
