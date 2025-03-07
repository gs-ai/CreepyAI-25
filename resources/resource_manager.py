# -*- coding: utf-8 -*-

"""
Resource manager for CreepyAI application.

This class provides a convenient interface for accessing application resources
loaded through the Qt resource system.
"""

import os
import logging
from typing import Optional
from PyQt5 import QtCore, QtGui

# Initialize logger
logger = logging.getLogger(__name__)

class ResourceManager:
    """
    Manager for application resources loaded through Qt's resource system.
    
    This class provides methods to access icons, images, and other resources
    that are embedded in the application through Qt's resource system.
    """
    
    def __init__(self):
        """Initialize the resource manager."""
        # Verify resources are loaded
        try:
            # Try to access a resource to check if resources are loaded
            test_path = ":/icons/app_icon.png"
            if not QtCore.QFile.exists(test_path):
                logger.warning("Resources not loaded or missing app_icon.png")
        except Exception as e:
            logger.error(f"Error checking resources: {e}")
    
    def get_icon(self, name: str) -> Optional[QtGui.QIcon]:
        """
        Get an icon from the resources.
        
        Args:
            name: Icon name (without path or extension)
            
        Returns:
            QIcon object or None if resource not found
        """
        try:
            path = f":/icons/{name}.png"
            if QtCore.QFile.exists(path):
                return QtGui.QIcon(path)
            else:
                logger.warning(f"Icon not found: {name}")
                return None
        except Exception as e:
            logger.error(f"Error loading icon {name}: {e}")
            return None
    
    def get_pixmap(self, path: str) -> Optional[QtGui.QPixmap]:
        """
        Get a pixmap from the resources.
        
        Args:
            path: Resource path (with prefix, e.g. ':/icons/app_icon.png')
            
        Returns:
            QPixmap object or None if resource not found
        """
        try:
            if QtCore.QFile.exists(path):
                return QtGui.QPixmap(path)
            else:
                logger.warning(f"Pixmap not found: {path}")
                return None
        except Exception as e:
            logger.error(f"Error loading pixmap {path}: {e}")
            return None
    
    def get_style(self, name: str) -> Optional[str]:
        """
        Get stylesheet content from resources.
        
        Args:
            name: Style name (without path or extension)
            
        Returns:
            Stylesheet content or None if not found
        """
        try:
            path = f":/styles/{name}.qss"
            file = QtCore.QFile(path)
            
            if not file.exists():
                logger.warning(f"Style not found: {name}")
                return None
                
            if file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
                stream = QtCore.QTextStream(file)
                content = stream.readAll()
                file.close()
                return content
            else:
                logger.error(f"Could not open style file: {path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading style {name}: {e}")
            return None
            
    def get_ui_file(self, name: str) -> Optional[str]:
        """
        Get UI file path for loading with uic.loadUi().
        
        Args:
            name: UI name (without path or extension)
            
        Returns:
            Path to UI file in resource system
        """
        path = f":/ui/{name}.ui"
        if QtCore.QFile.exists(path):
            return path
        else:
            logger.warning(f"UI file not found: {name}")
            return None
    
    def has_resource(self, path: str) -> bool:
        """
        Check if a resource exists.
        
        Args:
            path: Resource path (with prefix)
            
        Returns:
            True if the resource exists, False otherwise
        """
        return QtCore.QFile.exists(path)
    
    @staticmethod
    def list_resources(prefix: str) -> list:
        """
        List all resources under a specific prefix.
        
        Args:
            prefix: Resource prefix (e.g. ':/icons')
            
        Returns:
            List of resource paths
        """
        try:
            # Get the directory object
            dir_obj = QtCore.QDir(prefix)
            if not dir_obj.exists():
                logger.warning(f"Resource prefix not found: {prefix}")
                return []
                
            # Get files in the directory
            entries = dir_obj.entryList()
            result = [f"{prefix}/{entry}" for entry in entries if entry not in ['.', '..']]
            return result
            
        except Exception as e:
            logger.error(f"Error listing resources under {prefix}: {e}")
            return []
