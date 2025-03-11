"""
Stub for folium package when not installed.
This provides basic functionality to avoid import errors.
"""
import logging
import sys

logger = logging.getLogger('creepyai.utilities.folium_stub')

class FoliumNotInstalledError(ImportError):
    """Error raised when folium is not installed."""
    pass

class Map:
    """Stub Map class."""
    
    def __init__(self, location=None, zoom_start=10, tiles=None):
        """Initialize a map stub."""
        self.location = location
        self.zoom_start = zoom_start
        self.tiles = tiles
        logger.warning("Using folium stub implementation. Install folium for full map functionality.")
    
    def add_child(self, *args, **kwargs):
        """Stub for add_child method."""
        return self
    
    def save(self, *args, **kwargs):
        """Stub for save method."""
        logger.warning("Map save attempted but folium is not installed.")
        return None

class Marker:
    """Stub Marker class."""
    
    def __init__(self, *args, **kwargs):
        """Initialize a marker stub."""
        pass
    
    def add_to(self, *args, **kwargs):
        """Stub for add_to method."""
        return self

class Popup:
    """Stub Popup class."""
    
    def __init__(self, *args, **kwargs):
        """Initialize a popup stub."""
        pass

class Icon:
    """Stub Icon class."""
    
    def __init__(self, *args, **kwargs):
        """Initialize an icon stub."""
        pass

# Add the mocks to sys.modules to trick the import system
sys.modules['folium'] = sys.modules[__name__]
logger.info("Installed folium stub in sys.modules")

def install_folium_stub():
    """Install the folium stub to sys.modules."""
    sys.modules['folium'] = sys.modules[__name__]
    sys.modules['folium.map'] = sys.modules[__name__]
    sys.modules['folium.plugins'] = sys.modules[__name__]
    return True
