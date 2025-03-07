"""
CreepyAI Python Module

This module provides a simplified import system for CreepyAI components.
"""
import os
import sys
import importlib
import logging

logger = logging.getLogger(__name__)

# Add parent directory to Python path
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Define mappings for redirecting imports
_module_mappings = {
    'creepy.ui': 'ui',
    'creepy.models': 'models',
    'creepy.utilities': 'utilities',
    'creepy.plugins': 'plugins',
    'creepy.include': 'include',
    'creepy.resources': 'resources',
}

# Also handle submodules
for base_module in list(_module_mappings.keys()):
    target = _module_mappings[base_module]
    # Add mappings for common submodules
    for submodule in ['icons', 'utils', 'helpers']:
        _module_mappings[f"{base_module}.{submodule}"] = f"{target}.{submodule}"

# Implement module finder and loader for backwards compatibility
class CreepyFinder:
    """Custom module finder to redirect creepy.* imports to actual modules"""
    
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        """Find the module spec for creepy.* imports"""
        if fullname in _module_mappings:
            target_module = _module_mappings[fullname]
            try:
                # Try to import the target module
                target_module_spec = importlib.util.find_spec(target_module)
                if target_module_spec:
                    return target_module_spec
            except (ImportError, AttributeError):
                pass
        
        # Handle any creepy submodule
        parts = fullname.split('.')
        if len(parts) >= 2 and parts[0] == 'creepy':
            # Construct the target module name by removing 'creepy.'
            target_module = '.'.join(parts[1:])
            try:
                # Try to import the target module
                target_module_spec = importlib.util.find_spec(target_module)
                if target_module_spec:
                    return target_module_spec
            except (ImportError, AttributeError):
                pass
                
        return None

# Register the finder
sys.meta_path.insert(0, CreepyFinder)

# Expose key modules
try:
    from ui import CreepyUI
    from ui.creepy_map_view import MapView
    from models import Location, Project, ProjectTree
    from models.LocationsList import LocationsTableModel
    from utilities import GeneralUtilities, ExportUtils
except ImportError as e:
    logger.warning(f"Could not import some CreepyAI modules: {e}")
