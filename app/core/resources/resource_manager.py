"""
Resource Manager for CreepyAI.
Provides utilities for accessing various application resources.
"""
import os
import sys
import json
import logging
import shutil
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.core.path_utils import get_app_root, normalize_path, find_file
from app.core.utils import json_to_file, file_to_json

logger = logging.getLogger('creepyai.resources')

class ResourceManager:
    """Manages access to application resources."""
    
    def __init__(self):
        """Initialize the resource manager."""
        self.app_root = get_app_root()
        self.resources_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Define standard resource directories
        self.assets_dir = os.path.join(self.resources_dir, 'assets')
        self.templates_dir = os.path.join(self.resources_dir, 'templates')
        self.styles_dir = os.path.join(self.resources_dir, 'styles')
        self.html_dir = os.path.join(self.resources_dir, 'html')
        self.data_dir = os.path.join(self.resources_dir, 'data')
        
        # Create directories if they don't exist
        for dir_path in [self.assets_dir, self.templates_dir, self.styles_dir, 
                         self.html_dir, self.data_dir]:
            os.makedirs(dir_path, exist_ok=True)
            
        # Map of resource types to their directories
        self.resource_dirs = {
            'assets': self.assets_dir,
            'templates': self.templates_dir,
            'styles': self.styles_dir,
            'html': self.html_dir,
            'data': self.data_dir,
            'icons': os.path.join(self.assets_dir, 'icons'),
            'images': os.path.join(self.assets_dir, 'images'),
            'sounds': os.path.join(self.assets_dir, 'sounds'),
        }
        
        # Create asset subdirectories
        for subdir in ['icons', 'images', 'sounds']:
            os.makedirs(os.path.join(self.assets_dir, subdir), exist_ok=True)
            
        logger.debug(f"ResourceManager initialized with resources_dir: {self.resources_dir}")
        
    def get_resource_path(self, resource_type: str, resource_name: str) -> Optional[str]:
        """Get path to a resource.
        
        Args:
            resource_type: Type of resource (e.g., 'templates', 'icons')
            resource_name: Name of the resource file
            
        Returns:
            Full path to the resource or None if not found
        """
        if resource_type not in self.resource_dirs:
            logger.warning(f"Unknown resource type: {resource_type}")
            return None
            
        resource_dir = self.resource_dirs[resource_type]
        resource_path = os.path.join(resource_dir, resource_name)
        
        if os.path.exists(resource_path):
            return resource_path
            
        # Try legacy location in main resources dir
        legacy_path = os.path.join(self.app_root, 'resources', resource_name)
        if os.path.exists(legacy_path):
            logger.debug(f"Found resource {resource_name} in legacy location: {legacy_path}")
            return legacy_path
            
        logger.warning(f"Resource not found: {resource_type}/{resource_name}")
        return None
        
    def get_template(self, template_name: str) -> Optional[str]:
        """Get path to a template file.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Full path to the template or None if not found
        """
        return self.get_resource_path('templates', template_name)
        
    def get_style(self, style_name: str) -> Optional[str]:
        """Get path to a style file.
        
        Args:
            style_name: Name of the style
            
        Returns:
            Full path to the style or None if not found
        """
        return self.get_resource_path('styles', style_name)
        
    def get_html(self, html_name: str) -> Optional[str]:
        """Get path to an HTML file.
        
        Args:
            html_name: Name of the HTML file
            
        Returns:
            Full path to the HTML file or None if not found
        """
        return self.get_resource_path('html', html_name)
        
    def read_template(self, template_name: str) -> Optional[str]:
        """Read a template file and return its contents.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template contents or None if not found
        """
        template_path = self.get_template(template_name)
        if not template_path:
            return None
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading template {template_name}: {e}")
            return None
            
    def read_html(self, html_name: str) -> Optional[str]:
        """Read an HTML file and return its contents.
        
        Args:
            html_name: Name of the HTML file
            
        Returns:
            HTML contents or None if not found
        """
        html_path = self.get_html(html_name)
        if not html_path:
            return None
            
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading HTML {html_name}: {e}")
            return None
            
    def read_style(self, style_name: str) -> Optional[str]:
        """Read a style file and return its contents.
        
        Args:
            style_name: Name of the style file
            
        Returns:
            Style contents or None if not found
        """
        style_path = self.get_style(style_name)
        if not style_path:
            return None
            
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading style {style_name}: {e}")
            return None
            
    def load_json_data(self, data_name: str) -> Optional[Dict[str, Any]]:
        """Load JSON data file.
        
        Args:
            data_name: Name of the JSON file
            
        Returns:
            Parsed JSON data or None if not found/invalid
        """
        data_path = self.get_resource_path('data', data_name)
        if not data_path:
            return None
            
        return file_to_json(data_path)
        
    def save_json_data(self, data_name: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to a file.
        
        Args:
            data_name: Name of the JSON file
            data: Data to save
            
        Returns:
            True if saved successfully
        """
        if 'data' not in self.resource_dirs:
            return False
            
        data_dir = self.resource_dirs['data']
        os.makedirs(data_dir, exist_ok=True)
        data_path = os.path.join(data_dir, data_name)
        
        return json_to_file(data, data_path)
    
    def copy_resource(self, source_path: str, resource_type: str, resource_name: str) -> Optional[str]:
        """Copy an external resource into the resources directory.
        
        Args:
            source_path: Path to the source file
            resource_type: Type of resource (e.g., 'templates', 'icons')
            resource_name: Name to give the resource
            
        Returns:
            Path to the copied resource or None if failed
        """
        if resource_type not in self.resource_dirs:
            logger.warning(f"Unknown resource type: {resource_type}")
            return None
            
        if not os.path.exists(source_path):
            logger.error(f"Source file doesn't exist: {source_path}")
            return None
            
        dest_dir = self.resource_dirs[resource_type]
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, resource_name)
        
        try:
            shutil.copy2(source_path, dest_path)
            logger.debug(f"Copied resource from {source_path} to {dest_path}")
            return dest_path
        except Exception as e:
            logger.error(f"Error copying resource: {e}")
            return None
            
# Singleton instance
resource_manager = ResourceManager()
