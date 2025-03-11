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

# Define empty placeholders for modules that might not exist yet
__all__ = []

# Safely attempt to import and expose key modules
try:
    from ui import CreepyUI
    __all__.append('CreepyUI')
except ImportError:
    logger.debug("Could not import ui.CreepyUI")

try:
    from ui.creepy_map_view import MapView
    __all__.append('MapView')
except ImportError:
    logger.debug("Could not import ui.creepy_map_view.MapView")

try:
    from models import Location, Project, ProjectTree
    __all__.extend(['Location', 'Project', 'ProjectTree'])
except ImportError:
    logger.debug("Could not import models (Location, Project, ProjectTree)")

try:
    from app.models.LocationsList import LocationsTableModel
    __all__.append('LocationsTableModel')
except ImportError:
    logger.debug("Could not import app.models.LocationsList.LocationsTableModel")

try:
    from utilities import GeneralUtilities, ExportUtils
    __all__.extend(['GeneralUtilities', 'ExportUtils'])
except ImportError:
    logger.debug("Could not import utilities (GeneralUtilities, ExportUtils)")

def __init__(self):
    super().__init__()
    logger.info("Initializing CreepyAI Main Window...")
    try:
        # Initialize data structures
        self.current_project = None
        self.current_locations = []
        self.settings = {}
        
        # Set up the UI
        self.ui = Ui_CreepyAIMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CreepyAI - Geolocation OSINT AI Tool")
        
        # Create actions that are missing in the UI
        self.create_actions()
        
        # Initialize the map view
        self.setup_map_view()
        
        # Initialize plugins
        self.setup_plugins()
        
        # Connect UI signals
        self.connect_signals()
        
    except Exception as e:
        logger.error(f"Error initializing UI: {e}", exc_info=True)
        raise

def create_actions(self):
    """Create menu actions programmatically"""
    # File menu actions
    self.ui.actionNew = QAction("New Project", self)
    self.ui.actionOpen = QAction("Open Project", self)
    self.ui.actionSave = QAction("Save Project", self)
    self.ui.actionImport = QAction("Import Locations", self)
    self.ui.actionExport = QAction("Export Locations", self)
    self.ui.actionExit = QAction("Exit", self)
    
    # Tools menu actions
    self.ui.actionPluginManager = QAction("Plugin Manager", self)
    self.ui.actionSettings = QAction("Settings", self)
    
    # Add actions to menus if menus exist
    if hasattr(self.ui, 'menuFile'):
        self.ui.menuFile.addAction(self.ui.actionNew)
        self.ui.menuFile.addAction(self.ui.actionOpen)
        self.ui.menuFile.addAction(self.ui.actionSave)
        self.ui.menuFile.addSeparator()
        self.ui.menuFile.addAction(self.ui.actionImport)
        self.ui.menuFile.addAction(self.ui.actionExport)
        self.ui.menuFile.addSeparator()
        self.ui.menuFile.addAction(self.ui.actionExit)
        
    if hasattr(self.ui, 'menuTools'):
        self.ui.menuTools.addAction(self.ui.actionPluginManager)
        self.ui.menuTools.addAction(self.ui.actionSettings)
