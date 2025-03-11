"""
Project Model for CreepyAI
Defines the data structure for projects
"""

import os
import json
import logging
import zipfile
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal

from app.models.location_data import LocationDataModel, Location
from app.core.include.constants import PROJECT_EXTENSION

logger = logging.getLogger(__name__)

class Project(QObject):
    """Represents a CreepyAI project"""
    
    # Signals
    projectModified = pyqtSignal()
    projectSaved = pyqtSignal(str)  # path
    projectLoaded = pyqtSignal(str)  # path
    nameChanged = pyqtSignal(str)  # new name
    
    def __init__(self, name: str = "Untitled Project"):
        """
        Initialize a project
        
        Args:
            name: Project name
        """
        super().__init__()
        self.name = name
        self.description = ""
        self.created_date = datetime.now()
        self.modified_date = self.created_date
        self.author = ""
        self.path: Optional[str] = None
        self.tags: List[str] = []
        
        # Location data model
        self.locations = LocationDataModel()
        
        # Connect to location data model signals
        self.locations.dataChanged.connect(self._on_data_changed)
        
        # Project metadata
        self.metadata: Dict[str, Any] = {
            'version': '1.0',
            'created_with': 'CreepyAI',
            'notes': '',
        }
        
        # Remember if we've been modified since last save
        self.is_modified = False
        
        # Track loaded plugins
        self.active_plugins: List[str] = []
    
    def _on_data_changed(self) -> None:
        """Handle data changes in the location model"""
        self.is_modified = True
        self.modified_date = datetime.now()
        self.projectModified.emit()
    
    def set_name(self, name: str) -> None:
        """
        Set the project name
        
        Args:
            name: New project name
        """
        self.name = name
        self.is_modified = True
        self.modified_date = datetime.now()
        self.nameChanged.emit(name)
        self.projectModified.emit()
    
    def set_description(self, description: str) -> None:
        """
        Set the project description
        
        Args:
            description: New project description
        """
        self.description = description
        self.is_modified = True
        self.modified_date = datetime.now()
        self.projectModified.emit()
    
    def set_author(self, author: str) -> None:
        """
        Set the project author
        
        Args:
            author: Project author
        """
        self.author = author
        self.is_modified = True
        self.modified_date = datetime.now()
        self.projectModified.emit()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the project
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.is_modified = True
            self.modified_date = datetime.now()
            self.projectModified.emit()
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the project
        
        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.is_modified = True
            self.modified_date = datetime.now()
            self.projectModified.emit()
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Get project information
        
        Returns:
            Dictionary with project information
        """
        return {
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'path': self.path,
            'tags': self.tags,
            'location_count': self.locations.get_location_count(),
            'metadata': self.metadata,
            'active_plugins': self.active_plugins
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert project to dictionary
        
        Returns:
            Dictionary representation of the project
        """
        return {
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'created_date': self.created_date.isoformat(),
            'modified_date': self.modified_date.isoformat(),
            'tags': self.tags,
            'metadata': self.metadata,
            'active_plugins': self.active_plugins,
            'locations': [loc.to_dict() for loc in self.locations.get_all_locations()]
        }
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save the project
        
        Args:
            path: Path to save to (uses self.path if None)
            
        Returns:
            True if successful, False otherwise
        """
        # Use provided path or existing path
        if path:
            self.path = path
        elif not self.path:
            logger.error("No path specified for project save")
            return False
        
        # Ensure path has correct extension
        if not self.path.endswith(PROJECT_EXTENSION):
            self.path += PROJECT_EXTENSION
        
        try:
            # Create project data
            project_data = self.to_dict()
            
            # Save as JSON
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            
            # Mark as saved
            self.is_modified = False
            self.modified_date = datetime.now()
            self.projectSaved.emit(self.path)
            
            return True
        except Exception as e:
            logger.error(f"Error saving project to {self.path}: {e}")
            return False
    
    def save_archive(self, path: str) -> bool:
        """
        Save the project as a ZIP archive with related files
        
        Args:
            path: Path to save to
            
        Returns:
            True if successful, False otherwise
        """
        if not path.endswith('.zip'):
            path += '.zip'
        
        try:
            # Create a temporary directory for organizing files
            temp_dir = tempfile.mkdtemp()
            
            # Create a temporary file for the project data
            project_json_path = os.path.join(temp_dir, 'project.json')
            with open(project_json_path, 'w', encoding='utf-8') as f:
                # Save project data
                project_data = self.to_dict()
                json.dump(project_data, f, indent=2)
            
            # Create subdirectories for related files
            photos_dir = os.path.join(temp_dir, 'photos')
            os.makedirs(photos_dir, exist_ok=True)
            
            data_dir = os.path.join(temp_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Copy related files (photos, etc.)
            for location in self.locations.get_all_locations():
                # Copy photos
                for photo_path in location.photos:
                    if os.path.exists(photo_path):
                        photo_name = os.path.basename(photo_path)
                        dest_path = os.path.join(photos_dir, photo_name)
                        shutil.copy2(photo_path, dest_path)
            
            # Create ZIP archive
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all files in temp directory
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_file.write(file_path, arcname)
            
            # Remove temporary directory
            shutil.rmtree(temp_dir)
            
            return True
        except Exception as e:
            logger.error(f"Error creating project archive {path}: {e}")
            return False
    
    def export_to_format(self, path: str, format_type: str) -> bool:
        """
        Export project data to various formats
        
        Args:
            path: Path to export to
            format_type: Export format (json, csv, kml, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if format_type.lower() == 'json':
                # Export as GeoJSON
                geojson_data = self.locations.to_geojson()
                
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(geojson_data, f, indent=2)
                
                return True
                
            elif format_type.lower() == 'csv':
                # Export as CSV
                import csv
                
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(['id', 'latitude', 'longitude', 'timestamp', 'source', 'context', 'address'])
                    
                    # Write data
                    for location in self.locations.get_all_locations():
                        timestamp_str = ""
                        if location.timestamp:
                            timestamp_str = location.timestamp.isoformat()
                            
                        writer.writerow([
                            location.id,
                            location.latitude,
                            location.longitude,
                            timestamp_str,
                            location.source,
                            location.context,
                            location.address
                        ])
                
                return True
                
            elif format_type.lower() == 'kml':
                # Export as KML
                from app.exporters.kml_exporter import export_kml
                return export_kml(self.locations.get_all_locations(), path)
                
            elif format_type.lower() == 'gpx':
                # Export as GPX
                from app.exporters.gpx_exporter import export_gpx
                return export_gpx(self.locations.get_all_locations(), path)
                
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting project to {format_type}: {e}")
            return False
    
    def add_plugin(self, plugin_name: str) -> None:
        """
        Add a plugin to the active plugins list
        
        Args:
            plugin_name: Name of the plugin to add
        """
        if plugin_name not in self.active_plugins:
            self.active_plugins.append(plugin_name)
            self.is_modified = True
            self.modified_date = datetime.now()
            self.projectModified.emit()
    
    def remove_plugin(self, plugin_name: str) -> None:
        """
        Remove a plugin from the active plugins list
        
        Args:
            plugin_name: Name of the plugin to remove
        """
        if plugin_name in self.active_plugins:
            self.active_plugins.remove(plugin_name)
            self.is_modified = True
            self.modified_date = datetime.now()
            self.projectModified.emit()
    
    @classmethod
    def load(cls, path: str) -> Optional['Project']:
        """
        Load a project from a file
        
        Args:
            path: Path to load from
            
        Returns:
            Loaded project or None if loading failed
        """
        try:
            # Check if file exists
            if not os.path.isfile(path):
                logger.error(f"Project file not found: {path}")
                return None
            
            # Check if it's a ZIP archive
            if path.endswith('.zip'):
                return cls.load_archive(path)
            
            # Load JSON file
            with open(path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Create project
            project = cls(name=project_data.get('name', 'Untitled Project'))
            project.path = path
            project.description = project_data.get('description', '')
            project.author = project_data.get('author', '')
            
            # Parse dates
            if 'created_date' in project_data:
                try:
                    project.created_date = datetime.fromisoformat(project_data['created_date'])
                except (ValueError, TypeError):
                    project.created_date = datetime.now()
            
            if 'modified_date' in project_data:
                try:
                    project.modified_date = datetime.fromisoformat(project_data['modified_date'])
                except (ValueError, TypeError):
                    project.modified_date = datetime.now()
            
            project.tags = project_data.get('tags', [])
            project.metadata = project_data.get('metadata', {})
            project.active_plugins = project_data.get('active_plugins', [])
            
            # Load locations
            if 'locations' in project_data:
                for loc_data in project_data['locations']:
                    location = Location.from_dict(loc_data)
                    project.locations.add_location(location)
            
            # Mark as not modified (since we just loaded it)
            project.is_modified = False
            project.projectLoaded.emit(path)
            
            return project
        except Exception as e:
            logger.error(f"Error loading project from {path}: {e}")
            return None
    
    @classmethod
    def load_archive(cls, path: str) -> Optional['Project']:
        """
        Load a project from a ZIP archive
        
        Args:
            path: Path to load from
            
        Returns:
            Loaded project or None if loading failed
        """
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Extract the archive
            with zipfile.ZipFile(path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            # Load project.json
            project_file = os.path.join(temp_dir, 'project.json')
            if not os.path.isfile(project_file):
                logger.error(f"Project file not found in archive: {path}")
                return None
            
            # Load the project
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Create project
            project = cls(name=project_data.get('name', 'Untitled Project'))
            project.path = path
            project.description = project_data.get('description', '')
            project.author = project_data.get('author', '')
            
            # Parse dates
            if 'created_date' in project_data:
                try:
                    project.created_date = datetime.fromisoformat(project_data['created_date'])
                except (ValueError, TypeError):
                    project.created_date = datetime.now()
            
            if 'modified_date' in project_data:
                try:
                    project.modified_date = datetime.fromisoformat(project_data['modified_date'])
                except (ValueError, TypeError):
                    project.modified_date = datetime.now()
            
            project.tags = project_data.get('tags', [])
            project.metadata = project_data.get('metadata', {})
            project.active_plugins = project_data.get('active_plugins', [])
            
            # Load locations
            if 'locations' in project_data:
                for loc_data in project_data['locations']:
                    location = Location.from_dict(loc_data)
                    
                    # Check for related files in the archive
                    if location.photos:
                        updated_photos = []
                        for photo_path in location.photos:
                            photo_name = os.path.basename(photo_path)
                            archive_photo = os.path.join(temp_dir, 'photos', photo_name)
                            
                            if os.path.exists(archive_photo):
                                # Use the photo from the archive
                                updated_photos.append(archive_photo)
                            else:
                                # Keep the original path
                                updated_photos.append(photo_path)
                        
                        location.photos = updated_photos
                    
                    project.locations.add_location(location)
            
            # Mark as not modified (since we just loaded it)
            project.is_modified = False
            project.projectLoaded.emit(path)
            
            return project
        except Exception as e:
            logger.error(f"Error loading project archive from {path}: {e}")
            return None
        finally:
            try:
                # Clean up temporary directory if it exists
                if 'temp_dir' in locals() and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory: {e}")
