"""
Platform-specific utility functions for CreepyAI
"""

import os
import sys
import platform
import logging
from typing import Dict, Any, Tuple, Optional
import subprocess

logger = logging.getLogger(__name__)

def is_macos() -> bool:
    """Check if running on macOS"""
    return sys.platform == 'darwin'

def is_windows() -> bool:
    """Check if running on Windows"""
    return sys.platform == 'win32'

def is_linux() -> bool:
    """Check if running on Linux"""
    return sys.platform.startswith('linux')

def get_platform_info() -> Dict[str, Any]:
    """
    Get detailed information about the current platform
    
    Returns:
        Dictionary with platform information
    """
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }
    
    # Add PyQt information if available
    try:
        from PyQt5.QtCore import QT_VERSION_STR
        from PyQt5.Qt import PYQT_VERSION_STR
        
        info["qt_version"] = QT_VERSION_STR
        info["pyqt_version"] = PYQT_VERSION_STR
    except ImportError:
        info["qt_version"] = "Unknown"
        info["pyqt_version"] = "Unknown"
    
    return info

def get_user_home_dir() -> str:
    """
    Get the user's home directory path in a cross-platform way
    
    Returns:
        Path to user's home directory
    """
    return os.path.expanduser("~")

def get_app_data_dir() -> str:
    """
    Get the appropriate directory for storing application data
    
    Returns:
        Path to application data directory
    """
    system = platform.system()
    
    if system == "Windows":
        # On Windows, use %APPDATA%\CreepyAI
        return os.path.join(os.environ.get("APPDATA", get_user_home_dir()), "CreepyAI")
    elif system == "Darwin":
        # On macOS, use ~/Library/Application Support/CreepyAI
        return os.path.join(get_user_home_dir(), "Library", "Application Support", "CreepyAI")
    else:
        # On Linux/other, use ~/.config/creepyai
        return os.path.join(get_user_home_dir(), ".config", "creepyai")

def get_user_log_dir() -> str:
    """
    Get the appropriate directory for storing application logs
    
    Returns:
        Path to log directory
    """
    system = platform.system()
    
    if system == "Windows":
        # On Windows, use %APPDATA%\CreepyAI\logs
        return os.path.join(os.environ.get("APPDATA", get_user_home_dir()), "CreepyAI", "logs")
    elif system == "Darwin":
        # On macOS, use ~/Library/Logs/CreepyAI
        return os.path.join(get_user_home_dir(), "Library", "Logs", "CreepyAI")
    else:
        # On Linux/other, use ~/.local/share/creepyai/logs
        return os.path.join(get_user_home_dir(), ".local", "share", "creepyai", "logs")

def open_file_explorer(path: str) -> bool:
    """
    Open the file explorer at the specified path
    
    Args:
        path: Directory path to open
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
        return True
    except Exception as e:
        logger.error(f"Failed to open file explorer: {e}")
        return False

def get_executable_path() -> str:
    """
    Get the path of the current executable
    
    Returns:
        Path to the current executable
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys.executable
    else:
        # Running as script
        return sys.argv[0]

def check_admin_privileges() -> bool:
    """
    Check if the application is running with administrative privileges
    
    Returns:
        True if running with admin/root privileges, False otherwise
    """
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False
