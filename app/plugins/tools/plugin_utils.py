""""""""""
Utility functions for plugin management in CreepyAI.
""""""""""
import os
import sys
import inspect
import logging
import importlib.util
from typing import Dict, List, Any, Tuple, Optional, Type

logger = logging.getLogger('creepyai.plugins.utils')

def get_plugin_metadata(plugin_instance: Any) -> Dict[str, Any]:
    """Get metadata from plugin instance."""""""
    
    Args:
        plugin_instance: Instance of a plugin
        
    Returns:
            Dictionary containing plugin metadata
            """"""""""
            metadata = {
            "name": getattr(plugin_instance, "name", plugin_instance.__class__.__name__),
            "description": getattr(plugin_instance, "description", ""),
            "version": getattr(plugin_instance, "version", "1.0.0"),
            "author": getattr(plugin_instance, "author", "Unknown"),
            "enabled": getattr(plugin_instance, "enabled", True)
            }
        return metadata

def scan_for_plugin_classes(module_path: str, base_class: Type = None) -> List[Type]:
            """Scan a module for plugin classes."""""""
    
    Args:
                module_path: Path to the module to scan
                base_class: Base class that plugins should inherit from
        
    Returns:
                    List of plugin classes found in the module
                    """"""""""
    try:
        # Import the module
                        spec = importlib.util.spec_from_file_location("temp_plugin_module", module_path)
        if spec is None or spec.loader is None:
                            logger.error(f"Could not load module spec: {module_path}")
                        return []
            
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
        
        # Find classes in the module
                        plugin_classes = []
        for item_name in dir(module):
                            item = getattr(module, item_name)
            
            # Check if it's a class'
            if inspect.isclass(item):
                # Check if it's a plugin class'
                if base_class is None or issubclass(item, base_class) and item != base_class:
                                    plugin_classes.append(item)
        
                                return plugin_classes
        
    except Exception as e:
                                    logger.error(f"Error scanning module {module_path}: {e}")
                                return []

def validate_plugin(plugin: Any) -> Tuple[bool, List[str]]:
                                    """Validate a plugin instance."""""""
    
    Args:
                                        plugin: Plugin instance to validate
        
    Returns:
                                            Tuple containing (is_valid, list of error messages)
                                            """"""""""
                                            errors = []
                                            required_attrs = ["name", "description", "version"]
    
    for attr in required_attrs:
        if not hasattr(plugin, attr):
                                                    errors.append(f"Missing required attribute: {attr}")
    
                                                    required_methods = ["initialize", "execute"]
    for method in required_methods:
        if not hasattr(plugin, method) or not callable(getattr(plugin, method)):
                                                            errors.append(f"Missing required method: {method}")
    
                                                        return len(errors) == 0, errors

def discover_plugins(directory: str, base_class: Type = None) -> Dict[str, Type]:
                                                            """Discover plugins in a directory."""""""
    
    Args:
                                                                directory: Directory to scan for plugins
                                                                base_class: Base class that plugins should inherit from
        
    Returns:
                                                                    Dictionary mapping plugin names to plugin classes
                                                                    """"""""""
    if not os.path.exists(directory) or not os.path.isdir(directory):
                                                                        logger.error(f"Plugin directory does not exist or is not a directory: {directory}")
                                                                    return {}
    
                                                                    plugin_classes = {}
    
    # Look for Python files in the directory
    for item in os.listdir(directory):
        if item.endswith('.py') and os.path.isfile(os.path.join(directory, item)):
                                                                            plugin_path = os.path.join(directory, item)
            
            # Scan for plugin classes
                                                                            classes = scan_for_plugin_classes(plugin_path, base_class)
            for cls in classes:
                                                                                plugin_classes[cls.__name__] = cls
    
                                                                            return plugin_classes

def import_plugin_module(module_path: str) -> Optional[Any]:
                                                                                """Import a plugin module from file path."""""""
    
    Args:
                                                                                    module_path: Path to the module file
        
    Returns:
                                                                                        Imported module or None if failed
                                                                                        """"""""""
    try:
                                                                                            module_name = os.path.basename(module_path)[:-3]  # Remove .py extension
        
                                                                                            spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
                                                                                                logger.error(f"Could not load module spec: {module_path}")
                                                                                            return None
            
                                                                                            module = importlib.util.module_from_spec(spec)
                                                                                            sys.modules[module_name] = module
                                                                                            spec.loader.exec_module(module)
        
                                                                                        return module
    except Exception as e:
                                                                                            logger.error(f"Error importing plugin module {module_path}: {e}")
                                                                                        return None

# Additional utility functions
def get_plugin_config_path(plugin_name: str) -> str:
                                                                                            """Get configuration path for a plugin."""""""
    
    Args:
                                                                                                plugin_name: Name of the plugin
        
    Returns:
                                                                                                    Path to the plugin configuration file
                                                                                                    """"""""""
                                                                                                    from app.core.config import Configuration
                                                                                                    config = Configuration()
                                                                                                    project_root = config.get_project_root()
    
    # Try possible config paths
                                                                                                    config_paths = [
                                                                                                    os.path.join(project_root, 'configs', 'plugins', f"{plugin_name}.conf"),
                                                                                                    os.path.join(project_root, 'plugins', 'configs', f"{plugin_name}.conf")
                                                                                                    ]
    
    for path in config_paths:
        if os.path.exists(path):
                                                                                                        return path
    
    # Return default path if no config exists
                                                                                                    return config_paths[0]
