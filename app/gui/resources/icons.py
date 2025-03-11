"""
Icons resource file for CreepyAI
"""
import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

# Icon paths
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

# Ensure icons directory exists
os.makedirs(ICON_DIR, exist_ok=True)

# Default icon sizes
SMALL_ICON_SIZE = QSize(16, 16)
MEDIUM_ICON_SIZE = QSize(24, 24)
LARGE_ICON_SIZE = QSize(32, 32)

class Icons:
    """Icon manager for CreepyAI"""
    
    @staticmethod
    def get_icon(name, fallback=None):
        """Get an icon by name"""
        icon_path = os.path.join(ICON_DIR, f"{name}.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        elif fallback:
            return Icons.get_icon(fallback)
        else:
            # Return a blank icon
            return QIcon()
            
    @staticmethod
    def setup_action_icons(main_window):
        """Set up icons for action items in the main window"""
        ui = main_window.ui
        
        # File actions
        ui.actionNewProject.setIcon(Icons.get_icon("new"))
        ui.actionOpenProject.setIcon(Icons.get_icon("open"))
        ui.actionSaveProject.setIcon(Icons.get_icon("save"))
        ui.actionImportLocations.setIcon(Icons.get_icon("import"))
        ui.actionExportLocations.setIcon(Icons.get_icon("export"))
        ui.actionExit.setIcon(Icons.get_icon("exit"))
        
        # Map actions
        ui.actionAddLocation.setIcon(Icons.get_icon("location-add"))
        ui.actionZoomIn.setIcon(Icons.get_icon("zoom-in"))
        ui.actionZoomOut.setIcon(Icons.get_icon("zoom-out"))
        
        # Tool actions
        ui.actionManagePlugins.setIcon(Icons.get_icon("plugin"))
        ui.actionSettings.setIcon(Icons.get_icon("settings"))
        
        # Help actions
        ui.actionAbout.setIcon(Icons.get_icon("about"))
        ui.actionDocumentation.setIcon(Icons.get_icon("help"))
