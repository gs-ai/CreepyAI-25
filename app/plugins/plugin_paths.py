"""
Plugin path management for CreepyAI.
"""
import os
import sys
import glob
import logging
from typing import List, Optional

logger = logging.getLogger('creepyai.plugins.paths')

def get_plugin_directories() -> List[str]:
    """Get list of plugin directories.
    
    Returns:
        List of plugin directory paths
    """
    from app.core.config import Configuration
    config = Configuration()
    project_root = config.get_project_root()
    
    # Default plugin directories
    plugin_dirs = [
        os.path.join(project_root, 'plugins', 'src'),
        os.path.join(project_root, 'src', 'plugins')
    ]
    
    # Add user plugin directory if configured
    plugins_config = config.get('plugins')
    if plugins_config and 'user_plugins_path' in plugins_config:
        user_path = plugins_config['user_plugins_path']
        if user_path:
            if os.path.isabs(user_path):
                plugin_dirs.append(user_path)
            else:
                plugin_dirs.append(os.path.join(project_root, user_path))
    
    return plugin_dirs

def discover_plugin_paths(plugin_dirs: List[str] = None) -> List[str]:
    """Discover plugin file paths.
    
    Args:
        plugin_dirs: List of directories to search for plugins
        
    Returns:
        List of plugin file paths
    """
    if plugin_dirs is None:
        plugin_dirs = get_plugin_directories()
    
    plugin_paths = []
    
    for directory in plugin_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            # Find all Python files in the directory (non-recursive)
            for py_file in glob.glob(os.path.join(directory, "*.py")):
                if os.path.isfile(py_file) and not os.path.basename(py_file).startswith('_'):
                    plugin_paths.append(py_file)
                    
            # Find all plugin directories (containing __init__.py)
            for potential_pkg in glob.glob(os.path.join(directory, "*")):
                if (os.path.isdir(potential_pkg) and 
                    os.path.isfile(os.path.join(potential_pkg, "__init__.py"))):
                    plugin_paths.append(potential_pkg)
    
    return plugin_paths

def find_plugin_module(plugin_name: str) -> Optional[str]:
    """Find a plugin module by name.
    
    Args:
        plugin_name: Name of the plugin
        
    Returns:
        Path to the plugin module or None if not found
    """
    plugin_dirs = get_plugin_directories()
    
    for directory in plugin_dirs:
        # Check for direct .py file
        py_path = os.path.join(directory, f"{plugin_name}.py")
        if os.path.exists(py_path) and os.path.isfile(py_path):
            return py_path
            
        # Check for package directory
        pkg_path = os.path.join(directory, plugin_name)
        if (os.path.exists(pkg_path) and os.path.isdir(pkg_path) and 
            os.path.isfile(os.path.join(pkg_path, "__init__.py"))):
            return pkg_path
    
    return None
