"""
Path Utilities for CreepyAI
Handles standardized path management across the application
"""

import os
import sys
import logging
import platform
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def get_app_root() -> Path:
    """
    Get the application root directory
    
    Returns:
        Path to the application root directory
    """
    # If running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    
    # If running as a script
    return Path(__file__).resolve().parent.parent.parent

def get_user_data_dir() -> Path:
    r"""
    Get the user data directory for storing application data
    
    This follows platform-specific conventions:
    - Windows: %APPDATA%\CreepyAI
    - macOS: ~/Library/Application Support/CreepyAI
    - Linux: ~/.local/share/creepyai
    
    Returns:
        Path to user data directory
    """
    system = platform.system()
    
    if system == 'Windows':
        base_path = os.environ.get('APPDATA', '')
        if not base_path:
            base_path = os.path.expanduser('~')
        return Path(base_path) / 'CreepyAI'
    
    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'CreepyAI'
    
    else:  # Linux and others
        base_path = os.environ.get('XDG_DATA_HOME', '')
        if not base_path:
            base_path = os.path.expanduser('~/.local/share')
        return Path(base_path) / 'creepyai'

def get_user_config_dir() -> Path:
    r"""
    Get the user config directory for storing application configuration
    
    This follows platform-specific conventions:
    - Windows: %APPDATA%\CreepyAI
    - macOS: ~/Library/Application Support/CreepyAI
    - Linux: ~/.config/creepyai
    
    Returns:
        Path to user configuration directory
    """
    system = platform.system()
    
    if system == 'Windows':
        base_path = os.environ.get('APPDATA', '')
        if not base_path:
            base_path = os.path.expanduser('~')
        return Path(base_path) / 'CreepyAI'
    
    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'CreepyAI'
    
    else:  # Linux and others
        base_path = os.environ.get('XDG_CONFIG_HOME', '')
        if not base_path:
            base_path = os.path.expanduser('~/.config')
        return Path(base_path) / 'creepyai'

def get_user_log_dir() -> Path:
    r"""
    Get the user log directory for storing application logs
    
    This follows platform-specific conventions:
    - Windows: %APPDATA%\CreepyAI\logs
    - macOS: ~/Library/Logs/CreepyAI
    - Linux: ~/.local/share/creepyai/logs
    
    Returns:
        Path to user log directory
    """
    system = platform.system()
    
    if system == 'Windows':
        base_path = os.environ.get('APPDATA', '')
        if not base_path:
            base_path = os.path.expanduser('~')
        return Path(base_path) / 'CreepyAI' / 'logs'
    
    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Logs' / 'CreepyAI'
    
    else:  # Linux and others
        base_path = os.environ.get('XDG_DATA_HOME', '')
        if not base_path:
            base_path = os.path.expanduser('~/.local/share')
        return Path(base_path) / 'creepyai' / 'logs'

def get_user_cache_dir() -> Path:
    r"""
    Get the user cache directory for storing temporary data
    
    This follows platform-specific conventions:
    - Windows: %LOCALAPPDATA%\CreepyAI\cache
    - macOS: ~/Library/Caches/CreepyAI
    - Linux: ~/.cache/creepyai
    
    Returns:
        Path to user cache directory
    """
    system = platform.system()
    
    if system == 'Windows':
        base_path = os.environ.get('LOCALAPPDATA', '')
        if not base_path:
            base_path = os.path.expanduser('~\\AppData\\Local')
        return Path(base_path) / 'CreepyAI' / 'cache'
    
    elif system == 'Darwin':  # macOS
        return Path.home() / 'Library' / 'Caches' / 'CreepyAI'
    
    else:  # Linux and others
        base_path = os.environ.get('XDG_CACHE_HOME', '')
        if not base_path:
            base_path = os.path.expanduser('~/.cache')
        return Path(base_path) / 'creepyai'

def get_temp_dir() -> Path:
    """
    Get a temporary directory for the application
    
    Returns:
        Path to a temporary directory
    """
    temp_dir = Path(tempfile.gettempdir()) / 'creepyai'
    try:
        temp_dir.mkdir(exist_ok=True)
    except Exception as e:
        logger.warning(f"Failed to create temporary directory: {e}")
    
    return temp_dir

def get_resource_path(resource_name: str) -> Optional[Path]:
    """
    Get path to a resource file
    
    Args:
        resource_name: Resource file name or relative path
    
    Returns:
        Path to the resource or None if not found
    """
    # Check in resources directory first
    app_root = get_app_root()
    resource_path = app_root / 'app' / 'resources' / resource_name
    
    if resource_path.exists():
        return resource_path
    
    # Check in direct resources subdirectories
    for subdir in ['icons', 'images', 'map', 'templates']:
        resource_path = app_root / 'app' / 'resources' / subdir / resource_name
        if resource_path.exists():
            return resource_path
    
    logger.warning(f"Resource not found: {resource_name}")
    return None

def ensure_app_dirs() -> None:
    """
    Ensure all required application directories exist
    """
    dirs = [
        get_user_data_dir(),
        get_user_config_dir(),
        get_user_log_dir(),
        get_user_cache_dir(),
        get_temp_dir()
    ]
    
    for directory in dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
