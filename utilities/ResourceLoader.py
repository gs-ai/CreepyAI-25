#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import threading
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QFile, QIODevice, QObject

logger = logging.getLogger(__name__)

class ResourceLoader(QObject):
    """
    Singleton class for loading application resources.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    # Cache for loaded resources
    _icon_cache = {}
    _pixmap_cache = {}
    
    @classmethod
    def instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the resource loader."""
        super(ResourceLoader, self).__init__()
        
        # Standard resource paths
        self.resource_paths = {
            'images': ['resources/images', 'resources'],
            'icons': ['resources/icons', 'resources'],
            'styles': ['resources/styles'],
            'plugins': ['plugins'],
            'html': ['include'],
            'templates': ['resources/templates'],
        }
        
        # Check if we're in a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            self.is_bundled = True
            self.base_dir = sys._MEIPASS
        else:
            self.is_bundled = False
            self.base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
        logger.debug(f"ResourceLoader initialized with base_dir: {self.base_dir}")
    
    def get_icon(self, name, fallback=None):
        """
        Get a QIcon for the given name
        
        Args:
            name: Icon name (without extension)
            fallback: Fallback icon name if not found
            
        Returns:
            QIcon: The loaded icon
        """
        if name in self._icon_cache:
            return self._icon_cache[name]

        icon = QIcon(f":/creepy/{name}")
        if not icon.isNull():
            self._icon_cache[name] = icon
            return icon

        # Fix: Loop over list of paths (not tuple unpacking)
        for path in self.resource_paths['icons']:
            for ext in ['.png', '.svg', '.jpg']:
                file_path = os.path.join(self.base_dir, path, f"{name}{ext}")
                if os.path.exists(file_path):
                    icon = QIcon(file_path)
                    self._icon_cache[name] = icon
                    return icon

        if fallback and fallback != name:
            return self.get_icon(fallback)

        logger.warning(f"Icon not found: {name}")
        return QIcon()
    
    def get_pixmap(self, name, fallback=None):
        """
        Get a QPixmap for the given name
        
        Args:
            name: Pixmap name (without extension)
            fallback: Fallback pixmap name if not found
            
        Returns:
            QPixmap: The loaded pixmap
        """
        if name in self._pixmap_cache:
            return self._pixmap_cache[name]

        pixmap = QPixmap(f":/creepy/{name}")
        if not pixmap.isNull():
            self._pixmap_cache[name] = pixmap
            return pixmap

        # Fix: Loop over list of paths correctly
        for path in self.resource_paths['images']:
            for ext in ['.png', '.svg', '.jpg']:
                file_path = os.path.join(self.base_dir, path, f"{name}{ext}")
                if os.path.exists(file_path):
                    pixmap = QPixmap(file_path)
                    self._pixmap_cache[name] = pixmap
                    return pixmap

        if fallback and fallback != name:
            return self.get_pixmap(fallback)

        logger.warning(f"Pixmap not found: {name}")
        return QPixmap()
    
    def clear_cache(self):
        """Clear the resource cache"""
        self._icon_cache.clear()
        self._pixmap_cache.clear()
    
    def get_resource_path(self, resource_type, resource_name=None, extension=None):
        """
        Get the full path to a resource file.
        
        Args:
            resource_type: Type of resource (images, icons, etc.)
            resource_name: Name of the resource file (without extension)
            extension: File extension (optional)
            
        Returns:
            Full path to the resource file, or None if not found
        """
        if resource_type not in self.resource_paths:
            logger.warning(f"Unknown resource type: {resource_type}")
            return None
        
        # If resource_name is None, return the first valid directory for this resource type
        if resource_name is None:
            for path in self.resource_paths[resource_type]:
                full_path = os.path.join(self.base_dir, path)
                if os.path.isdir(full_path):
                    return full_path
            return None
        
        # Try all possible paths for this resource type
        for path in self.resource_paths[resource_type]:
            file_path = os.path.join(self.base_dir, path, f"{resource_name}{extension or ''}")
            if os.path.exists(file_path):
                return file_path
        
        return None

    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        base_dirs = [
            'projects', 
            'temp', 
            'plugins', 
            'include',
            'resources'
        ]
        
        for directory in base_dirs:
            dir_path = os.path.join(self.base_dir, directory)
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {str(e)}")
                    
        # Also ensure log directory exists
        log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        return True