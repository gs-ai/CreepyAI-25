"""
Import helper utilities for CreepyAI.
Provides utilities for dynamic module importing and path management.
"""
import os
import sys
import importlib
import importlib.util
import logging
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

# Make sure we can import from path_utils with absolute path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from app.core.path_utils import normalize_path, get_app_root

logger = logging.getLogger('creepyai.core.imports')

# Define ensure_module_paths since it's imported before being defined
def ensure_module_paths() -> None:
    """Ensure core module paths are available for imports."""
    app_root = get_app_root()
    
    # Add app root to Python path if not already there
    if app_root not in sys.path:
        sys.path.insert(0, app_root)
    
    # Add src directory to Python path
    src_dir = os.path.join(app_root, 'src')
    if os.path.exists(src_dir) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)

def import_module_from_path(module_name: str, file_path: str) -> Optional[ModuleType]:
    """Import a module from a file path.
    
    Args:
        module_name: Name to give the module
        file_path: Path to the module file
        
    Returns:
        Imported module or None if import failed
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Module file not found: {file_path}")
            return None
        
        # Use Python's import machinery to load the module
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            logger.error(f"Failed to create module spec for {file_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module  # Register in sys.modules
        spec.loader.exec_module(module)
        
        return module
    except Exception as e:
        logger.error(f"Error importing module {module_name} from {file_path}: {e}")
        return None

def find_class_in_module(module: ModuleType, base_class: type) -> Optional[type]:
    """Find a class in a module that inherits from a base class.
    
    Args:
        module: Module to search in
        base_class: Base class to look for
        
    Returns:
        Class that inherits from base_class or None if not found
    """
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and
            attr.__module__ == module.__name__ and
            issubclass(attr, base_class) and
            attr != base_class):
            return attr
            
    return None

def dynamic_import(name: str) -> Optional[Any]:
    """Dynamically import a module or object by name.
    
    Args:
        name: Module or object name (e.g., 'os.path' or 'os.path.join')
        
    Returns:
        Imported module/object or None if import failed
    """
    try:
        components = name.split('.')
        
        # First import the base module
        base_module = importlib.import_module(components[0])
        current = base_module
        
        # Then traverse the object hierarchy
        for component in components[1:]:
            current = getattr(current, component)
            
        return current
    except (ImportError, AttributeError) as e:
        logger.error(f"Error importing {name}: {e}")
        return None

def ensure_imports() -> None:
    """Ensure proper import paths are set up."""
    # Make sure module paths are available
    ensure_module_paths()
    
    # Add commonly used directories to Python path
    app_root = get_app_root()
    
    paths_to_add = [
        os.path.join(app_root, 'src'),
        os.path.join(app_root, 'plugins'),
        os.path.join(app_root, 'plugins', 'src')
    ]
    
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            logger.debug(f"Added {path} to Python path")

def reload_module(module_name: str) -> Optional[ModuleType]:
    """Reload a module by name.
    
    Args:
        module_name: Name of the module to reload
        
    Returns:
        Reloaded module or None if failed
    """
    try:
        if module_name in sys.modules:
            return importlib.reload(sys.modules[module_name])
        else:
            return importlib.import_module(module_name)
    except Exception as e:
        logger.error(f"Error reloading module {module_name}: {e}")
        return None

def get_module_dependencies(module: ModuleType) -> List[str]:
    """Get list of dependencies for a module.
    
    Args:
        module: Module to analyze
        
    Returns:
        List of dependency module names
    """
    dependencies = set()
    
    # Check module's __all__ attribute if it exists
    if hasattr(module, '__all__'):
        for name in module.__all__:
            if hasattr(module, name):
                obj = getattr(module, name)
                if isinstance(obj, ModuleType) and obj.__name__ != module.__name__:
                    dependencies.add(obj.__name__)
    
    # Look at all attributes in module's namespace
    for attr_name in dir(module):
        if attr_name.startswith('__'):
            continue
            
        try:
            attr = getattr(module, attr_name)
            if isinstance(attr, ModuleType) and attr.__name__ != module.__name__:
                dependencies.add(attr.__name__)
        except Exception:
            pass
    
    return sorted(list(dependencies))

def is_plugin_module(module: ModuleType) -> bool:
    """Check if a module is a plugin module.
    
    Args:
        module: Module to check
        
    Returns:
        True if module appears to be a plugin
    """
    # Check if the module has any classes that look like plugins
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type):
            if any(base.__name__.endswith('Plugin') for base in attr.__mro__):
                return True
                
            # Check for common plugin method patterns
            if hasattr(attr, 'execute') and callable(getattr(attr, 'execute')):
                return True
                
            if hasattr(attr, 'run') and callable(getattr(attr, 'run')):
                return True
    
    return False
