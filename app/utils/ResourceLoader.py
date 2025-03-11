#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import threading
import json
from functools import lru_cache
from typing import Dict, Any, Optional, List
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QFile, QIODevice, QObject
from pathlib import Path

# Use absolute import path for better reliability
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from app.core.path_utils import normalize_path, get_app_root, ensure_app_dirs

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
    
    def __new__(cls, *args, **kwargs):
        # Singleton pattern with thread safety
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ResourceLoader, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, base_path=None):
        if self._initialized:
            return
            
        super().__init__()
        self.logger = logging.getLogger('ResourceLoader')
        self.app_root = get_app_root()
        
        # Ensure all application directories exist
        app_dirs = ensure_app_dirs()
        
        # Normalize base path
        if base_path:
            self.base_path = normalize_path(base_path)
        else:
            self.base_path = os.path.join(self.app_root, 'resources')
            
        self._cache: Dict[str, Any] = {}
        self._resource_paths = {}
        
        # Use standardized resource paths with deterministic fallbacks
        self.resource_paths = {
            'images': [
                os.path.join(self.app_root, 'resources', 'assets', 'images'),
                os.path.join(self.app_root, 'resources', 'images'),
                os.path.join(self.app_root, 'assets', 'images'),
                os.path.join(self.app_root, 'resources')
            ],
            'icons': [
                os.path.join(self.app_root, 'resources', 'assets', 'icons'),
                os.path.join(self.app_root, 'resources', 'icons'),
                os.path.join(self.app_root, 'assets', 'icons'),
                os.path.join(self.app_root, 'assets', 'icons', 'ui')
            ],
            'styles': [
                os.path.join(self.app_root, 'resources', 'styles'),
                os.path.join(self.app_root, 'resources', 'css')
            ],
            'plugins': [
                os.path.join(self.app_root, 'plugins', 'src'),
                os.path.join(self.app_root, 'plugins')
            ],
            'html': [
                os.path.join(self.app_root, 'include'),
                os.path.join(self.app_root, 'resources', 'html'),
                os.path.join(self.app_root, 'src', 'include')
            ],
            'templates': [
                os.path.join(self.app_root, 'resources', 'templates'),
                os.path.join(self.app_root, 'templates')
            ],
        }
        
        # Ensure all resource directories exist
        for path_list in self.resource_paths.values():
            for path in path_list:
                os.makedirs(path, exist_ok=True)
        
        # Check if we're in a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            self.is_bundled = True
            self.base_dir = sys._MEIPASS
        else:
            self.is_bundled = False
            self.base_dir = self.app_root
        
        self._scan_resources()
        self._initialized = True
        logger.debug(f"ResourceLoader initialized with base_dir: {self.base_dir}")
    
    def _scan_resources(self):
        """Scan and index all available resources for faster lookup"""
        self.logger.debug(f"Scanning resources in {self.base_path}")
        
        # Scan all resource directories and index files
        resource_dirs = set()
        for path_list in self.resource_paths.values():
            resource_dirs.update(path_list)
        
        # Add base path and app root resources
        resource_dirs.add(self.base_path)
        resource_dirs.add(os.path.join(self.app_root, 'resources'))
        
        for resource_dir in resource_dirs:
            if os.path.exists(resource_dir):
                for root, dirs, files in os.walk(resource_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Store both the full path and relative paths
                        self._resource_paths[file] = full_path
                        
                        # Add path relative to resource directory
                        rel_path = os.path.relpath(full_path, resource_dir)
                        self._resource_paths[rel_path] = full_path
                        
                        # Also index without extension for convenience
                        name, ext = os.path.splitext(file)
                        self._resource_paths[name] = full_path
        
        self.logger.info(f"Indexed {len(self._resource_paths)} resources")
    
    @lru_cache(maxsize=128)
    def get_resource_path(self, resource_name: str) -> Optional[str]:
        """Get resource path with caching"""
        if resource_name in self._resource_paths:
            return self._resource_paths[resource_name]
            
        # Try partial matching
        for path in self._resource_paths:
            if path.endswith(resource_name):
                return self._resource_paths[path]
                
        self.logger.warning(f"Resource not found: {resource_name}")
        return None
        
    def load_json_resource(self, resource_name: str) -> Optional[Dict]:
        """Load and parse a JSON resource with error handling"""
        path = self.get_resource_path(resource_name)
        if not path:
            return None
            
        # Check cache first
        if path in self._cache:
            return self._cache[path]
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Cache the result
                self._cache[path] = data
                return data
        except Exception as e:
            self.logger.error(f"Error loading JSON resource {resource_name}: {e}")
            return None
    
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

        # Try finding the icon in multiple locations
        for path in self.resource_paths['icons']:
            for ext in ['.png', '.svg', '.jpg']:
                # Try multiple naming conventions
                file_paths = [
                    os.path.join(path, f"{name}{ext}"),
                    os.path.join(path, f"{name.lower()}{ext}"),
                    os.path.join(path, f"{name.replace('_', '-')}{ext}")
                ]
                
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        icon = QIcon(file_path)
                        if not icon.isNull():
                            self._icon_cache[name] = icon
                            return icon

        # Use explicit path if in resource paths
        if name in self._resource_paths:
            file_path = self._resource_paths[name]
            if os.path.exists(file_path):
                icon = QIcon(file_path)
                if not icon.isNull():
                    self._icon_cache[name] = icon
                    return icon

        if fallback and fallback != name:
            return self.get_icon(fallback)

        self.logger.warning(f"Icon not found: {name}")
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
        self._cache.clear()
        # Clear the lru_cache
        self.get_resource_path.cache_clear()
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        # Use the standardized directory structure
        app_dirs = ensure_app_dirs()
        
        # Also ensure log directory exists
        log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        return True
    
    def get_plugin_resource_path(self, plugin_name: str, resource_name: str) -> Optional[str]:
        """Get path to a plugin-specific resource.
        
        Args:
            plugin_name: Name of the plugin
            resource_name: Name of the resource
            
        Returns:
            Path to resource or None if not found
        """
        # Check in plugin-specific directories
        plugin_resource_paths = [
            os.path.join(self.app_root, 'plugins', plugin_name, 'resources', resource_name),
            os.path.join(self.app_root, 'plugins', 'resources', plugin_name, resource_name),
            os.path.join(self.app_root, 'resources', 'plugins', plugin_name, resource_name)
        ]
        
        for path in plugin_resource_paths:
            if os.path.exists(path):
                return path
                
        # If not found, try standard resource lookup
        return self.get_resource_path(resource_name)