"""
Icon resources for CreepyAI application.
Provides central access to all application icons.
"""
import os
import sys
from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

# Base paths
current_dir = os.path.dirname(os.path.abspath(__file__))
app_root = str(Path(current_dir).parent.parent)
icons_dir = os.path.join(app_root, "resources", "icons")
fallback_icon = os.path.join(icons_dir, "default.png")

# Ensure the icons directory exists
if not os.path.exists(icons_dir):
    os.makedirs(icons_dir, exist_ok=True)

class Icons:
    """Basic icons class for CreepyAI."""
    
    @staticmethod
    def get_icon(name):
        """Return path to an icon."""
        from app.core.config import Configuration
        config = Configuration()
        project_root = config.get_project_root()
        return f"{project_root}/resources/icons/{name}.png"
    
    @staticmethod
    def get_pixmap(name: str, size: int = 16) -> QPixmap:
        """Get a pixmap by name
        
        Args:
            name: Icon name (without extension)
            size: Requested size in pixels
            
        Returns:
            QPixmap instance
        """
        icon = Icons.get_icon(name)
        return icon.pixmap(QSize(size, size))
        
    # Common application icons
    @staticmethod
    def app_icon() -> QIcon:
        return Icons.get_icon("app")
        
    @staticmethod
    def new() -> QIcon:
        return Icons.get_icon("new")
        
    @staticmethod
    def open() -> QIcon:
        return Icons.get_icon("open")
    
    @staticmethod
    def save() -> QIcon:
        return Icons.get_icon("save")
    
    @staticmethod
    def settings() -> QIcon:
        return Icons.get_icon("settings")
    
    @staticmethod
    def export() -> QIcon:
        return Icons.get_icon("export")
    
    @staticmethod
    def import_icon() -> QIcon:
        return Icons.get_icon("import")
        
    @staticmethod
    def exit() -> QIcon:
        return Icons.get_icon("exit")
        
    @staticmethod
    def help() -> QIcon:
        return Icons.get_icon("help")
        
    @staticmethod
    def about() -> QIcon:
        return Icons.get_icon("about")
        
    @staticmethod
    def refresh() -> QIcon:
        return Icons.get_icon("refresh")
        
    @staticmethod
    def search() -> QIcon:
        return Icons.get_icon("search")
        
    @staticmethod
    def plugin() -> QIcon:
        return Icons.get_icon("plugin")
        
    @staticmethod
    def map() -> QIcon:
        return Icons.get_icon("map")
        
    @staticmethod
    def location() -> QIcon:
        return Icons.get_icon("location")
        
    @staticmethod
    def person() -> QIcon:
        return Icons.get_icon("person")
        
    @staticmethod
    def info() -> QIcon:
        return Icons.get_icon("info")
        
    @staticmethod
    def warning() -> QIcon:
        return Icons.get_icon("warning")
        
    @staticmethod
    def error() -> QIcon:
        return Icons.get_icon("error")

# Create basic default icon if it doesn't exist
if not os.path.exists(fallback_icon):
    try:
        from PyQt5.QtGui import QPainter, QColor
        from PyQt5.QtCore import Qt
        
        # Create a simple default icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(60, 60, 60))
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRect(8, 8, 48, 48)
        painter.end()
        
        # Save the default icon
        os.makedirs(os.path.dirname(fallback_icon), exist_ok=True)
        pixmap.save(fallback_icon)
    except Exception as e:
        print(f"Failed to create default icon: {e}")
