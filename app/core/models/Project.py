#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Project model handling for CreepyAI.
Supports both JSON and shelve formats for backwards compatibility.
"""
import os
import json
import uuid
import logging
import datetime
import shelve
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger('creepyai.models.project')

# Try to import Location class, use placeholder if not available
try:
    from .Location import Location
except ImportError:
    class Location:
        """Placeholder Location class"""
        def __init__(self):
            self.latitude = 0.0
            self.longitude = 0.0
            self.datetime = None
            self.context = ""
            self.plugin = ""
            self.shortName = ""
            self.infowindow = ""
            self.visible = True
            self.id = None

class Project:
    """
    Unified project class for CreepyAI supporting both new JSON format
    and legacy shelve format for backwards compatibility.
    """
    
    def __init__(self, name=None, target=None, project_id=None, path=None):
        """
        Initialize a new project
        
        Args:
            name: Project name
            target: Target name or identifier
            project_id: Unique project ID (generated if not provided)
            path: Path to project file if loading an existing project
        """
        # Modern attributes
        self.name = name or ""
        self.target = target or name or ""
        self.project_id = project_id or str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        self.locations = []
        self.metadata = {}
        self.notes = ""
        self.tags = []
        self.settings = {}
        self.path = path
        self.plugin_data = {}
        
        # Legacy attributes for backward compatibility
        self.projectName = name or ""
        self.projectKeywords = []
        self.projectDescription = ""
        self.dateCreated = self.created_at
        self.dateEdited = self.modified_at
        self.enabledPlugins = []
        self.viewSettings = {}
        self.selectedTargets = []
        self.analysis = None
        self.isAnalysisRunning = False
        
        # Load project if path is provided
        if path:
            self.load(path)
    
    def is_modified(self):
        """Check if project has been modified since last save"""
        return self.modified_at > self.dateEdited
    
    def set_project_dir(self, project_dir):
        """Set project directory and default path"""
        self.path = os.path.join(project_dir, f"{self.name}.json")
        return self.path
    
    def load(self, path):
        """
        Load a project from disk in either JSON or shelve format
        
        Args:
            path: Path to the project file (.json or .db)
            
        Returns:
            bool: True if loaded successfully
        """
        self.path = path
        
        # Determine format from file extension
        if path.endswith('.json'):
            return self._load_json(path)
        else:
            return self._load_shelve(path)
    
    def _load_shelve(self, path):
        """Load from legacy shelve database format"""
        try:
            # Remove .db extension if present
            if path.endswith('.db'):
                path = path[:-3]
                
            # Open the shelve database
            with shelve.open(path) as db:
                # Load basic project info
                self.projectName = db.get('projectName', "")
                self.name = self.projectName
                self.projectKeywords = db.get('projectKeywords', [])
                self.tags = self.projectKeywords
                self.projectDescription = db.get('projectDescription', "")
                self.notes = self.projectDescription
                self.dateCreated = db.get('dateCreated', datetime.datetime.now())
                self.created_at = self.dateCreated
                self.dateEdited = db.get('dateEdited', datetime.datetime.now())
                self.modified_at = self.dateEdited
                
                # Load plugin and target configuration
                self.enabledPlugins = db.get('enabledPlugins', [])
                self.selectedTargets = db.get('selectedTargets', [])
                if self.selectedTargets and not self.target:
                    self.target = self.selectedTargets[0]
                self.viewSettings = db.get('viewSettings', {})
                self.settings = self.viewSettings
                
                # Load locations with proper instantiation
                locations_data = db.get('locations', [])
                self.locations = self._convert_locations(locations_data)
                
                # Load analysis data if any
                self.analysis = db.get('analysis', None)
                self.metadata['analysis'] = self.analysis
            
            logger.info(f"Project loaded from shelve: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load project from {path}: {str(e)}")
            return False
    
    def _load_json(self, path):
        """Load from modern JSON format"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Set attributes from JSON data
            self.name = data.get('name', "")
            self.projectName = self.name
            self.target = data.get('target', "")
            self.project_id = data.get('project_id', str(uuid.uuid4()))
            
            # Handle timestamps
            self._parse_timestamps(data)
                
            # Load other data
            self.locations = data.get('locations', [])
            self.metadata = data.get('metadata', {})
            self.notes = data.get('notes', '')
            self.projectDescription = self.notes
            self.tags = data.get('tags', [])
            self.projectKeywords = self.tags
            self.settings = data.get('settings', {})
            self.viewSettings = self.settings
            self.plugin_data = data.get('plugin_data', {})
            
            # Handle selectedTargets for compatibility
            if 'selectedTargets' in data:
                self.selectedTargets = data.get('selectedTargets', [])
            elif self.target:
                self.selectedTargets = [self.target]
                
            logger.info(f"Project loaded from JSON: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load JSON project: {e}")
            return False

    def _parse_timestamps(self, data):
        """Parse timestamp data from JSON"""
        if 'created_at' in data:
            try:
                if isinstance(data['created_at'], str):
                    self.created_at = datetime.datetime.fromisoformat(data['created_at'])
                else:
                    self.created_at = datetime.datetime.now()
            except (ValueError, TypeError):
                self.created_at = datetime.datetime.now()
                logger.warning(f"Invalid created_at format in project data")
                
        if 'modified_at' in data:
            try:
                if isinstance(data['modified_at'], str):
                    self.modified_at = datetime.datetime.fromisoformat(data['modified_at'])
                else:
                    self.modified_at = datetime.datetime.now()
            except (ValueError, TypeError):
                self.modified_at = datetime.datetime.now()
                logger.warning(f"Invalid modified_at format in project data")
                
        self.dateCreated = self.created_at
        self.dateEdited = self.modified_at
    
    def _convert_locations(self, locations_data):
        """Convert location data to the appropriate format"""
        converted_locations = []
        for loc in locations_data:
            if isinstance(loc, dict):
                # Already a dict, use as is
                converted_locations.append(loc)
            else:
                # Convert Location object to dict
                location_dict = {
                    'latitude': getattr(loc, 'latitude', 0),
                    'longitude': getattr(loc, 'longitude', 0),
                    'datetime': getattr(loc, 'datetime', None),
                    'timestamp': getattr(loc, 'datetime', None),
                    'context': getattr(loc, 'context', ""),
                    'plugin': getattr(loc, 'plugin', ""),
                    'name': getattr(loc, 'shortName', ""),
                    'description': getattr(loc, 'infowindow', ""),
                    'visible': getattr(loc, 'visible', True),
                    'id': getattr(loc, 'id', str(uuid.uuid4()))
                }
                converted_locations.append(location_dict)
        return converted_locations
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save project to file in either JSON (preferred) or shelve format
        
        Args:
            path: Path to save project to (.json or .db)
            
        Returns:
            bool: True if saved successfully
        """
        if path:
            self.path = path
            
        if not self.path:
            # Generate a default path in the projects directory
            projects_dir = os.path.join(os.getcwd(), 'projects')
            os.makedirs(projects_dir, exist_ok=True)
            self.path = os.path.join(projects_dir, f"{self.name}.json")
            
        # Update timestamps
        self.modified_at = datetime.datetime.now()
        self.dateEdited = self.modified_at
            
        # Save based on file extension
        if self.path.endswith('.json'):
            return self._save_json(self.path)
        else:
            return self._save_shelve(self.path)
    
    def _save_shelve(self, path):
        """Save to shelve database (legacy format)"""
        try:
            # Remove .db extension if present
            if path.endswith('.db'):
                path = path[:-3]
                
            # Convert locations to a format suitable for shelve
            locations_to_save = []
            for loc in self.locations:
                if isinstance(loc, dict):
                    # Create Location object 
                    location = Location()
                    location.latitude = loc.get('latitude', 0)
                    location.longitude = loc.get('longitude', 0)
                    location.datetime = loc.get('datetime') or loc.get('timestamp')
                    location.context = loc.get('context', "")
                    location.plugin = loc.get('plugin', "")
                    location.shortName = loc.get('name', "") or loc.get('shortName', "")
                    location.infowindow = loc.get('description', "") or loc.get('infowindow', "")
                    location.visible = loc.get('visible', True)
                    location.id = loc.get('id', str(uuid.uuid4()))
                    locations_to_save.append(location)
                else:
                    # Already a Location object
                    locations_to_save.append(loc)
            
            # Store data in shelve database
            with shelve.open(path) as db:
                db['projectName'] = self.name
                db['projectKeywords'] = self.tags or self.projectKeywords
                db['projectDescription'] = self.notes or self.projectDescription
                db['dateCreated'] = self.created_at
                db['dateEdited'] = self.modified_at
                db['enabledPlugins'] = self.enabledPlugins
                db['selectedTargets'] = self.selectedTargets or [self.target] if self.target else []
                db['locations'] = locations_to_save
                db['viewSettings'] = self.settings or self.viewSettings
                db['analysis'] = self.metadata.get('analysis') or self.analysis
            
            logger.info(f"Project saved to shelve: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project to shelve: {str(e)}")
            return False
    
    def _save_json(self, path):
        """Save to JSON file (modern format)"""
        try:
            # Ensure project directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Create data directory if needed
            data_dir = os.path.join(os.path.dirname(path), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Prepare data to save
            data = self.to_dict()
            
            # Save as JSON
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Project saved to JSON: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project to JSON: {str(e)}")
            return False
    
    def delete(self):
        """
        Delete the project files from disk.
        
        Returns:
            bool: True if successfully deleted
        """
        if not self.path:
            logger.warning("No path specified for project deletion")
            return False
            
        try:
            if self.path.endswith('.json'):
                if os.path.exists(self.path):
                    os.remove(self.path)
            else:
                # Handle shelve files
                base_path = self.path
                if base_path.endswith('.db'):
                    base_path = base_path[:-3]
                    
                for ext in ['', '.db', '.dat', '.bak', '.dir']:
                    if os.path.exists(base_path + ext):
                        os.remove(base_path + ext)
            
            logger.info(f"Project deleted: {self.path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {self.path}: {str(e)}")
            return False
    
    @staticmethod
    def getProjectsList():
        """Legacy method for backward compatibility"""
        return Project.get_projects_list()
    
    @staticmethod
    def get_projects_list():
        """
        Get a list of available projects.
        
        Returns:
            List of dictionaries with project info
        """
        projects = []
        projects_dir = os.path.join(os.getcwd(), 'projects')
        
        # Create directory if it doesn't exist
        os.makedirs(projects_dir, exist_ok=True)
        
        try:
            # Find all project files (both .db and .json)
            for filename in os.listdir(projects_dir):
                project_info = None
                
                # Handle shelve database files
                if filename.endswith('.db'):
                    project_name = filename[:-3]  # Remove .db extension
                    project_path = os.path.join(projects_dir, project_name)
                    
                    try:
                        with shelve.open(project_path) as db:
                            project_info = {
                                'name': db.get('projectName', project_name),
                                'date': db.get('dateEdited', datetime.datetime.now()),
                                'path': os.path.join(projects_dir, filename),
                                'type': 'shelve'
                            }
                    except Exception:
                        # Include the project even if we can't read its details
                        project_info = {
                            'name': project_name,
                            'date': datetime.datetime.now(),
                            'path': os.path.join(projects_dir, filename),
                            'type': 'shelve'
                        }
                
                # Handle JSON project files
                elif filename.endswith('.json'):
                    try:
                        with open(os.path.join(projects_dir, filename), 'r') as f:
                            data = json.load(f)
                            
                        # Parse date string to datetime
                        modified_date = datetime.datetime.now()
                        if 'modified_at' in data:
                            try:
                                if isinstance(data['modified_at'], str):
                                    modified_date = datetime.datetime.fromisoformat(data['modified_at'])
                            except ValueError:
                                pass
                                
                        project_info = {
                            'name': data.get('name', filename[:-5]),  # Remove .json extension
                            'date': modified_date,
                            'path': os.path.join(projects_dir, filename),
                            'type': 'json'
                        }
                    except Exception:
                        # Include the project even if we can't read its details
                        project_info = {
                            'name': filename[:-5],  # Remove .json extension
                            'date': datetime.datetime.now(),
                            'path': os.path.join(projects_dir, filename),
                            'type': 'json'
                        }
                
                # Add project to list if we got info
                if project_info:
                    projects.append(project_info)
            
            # Sort projects by date
            projects.sort(key=lambda x: x['date'], reverse=True)
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects list: {str(e)}")
            return []
    
    def add_location(self, location):
        """
        Add a location to the project
        
        Args:
            location: Location object or dictionary with location data
        """
        if isinstance(location, dict):
            # Ensure the location has required fields
            if 'latitude' not in location or 'longitude' not in location:
                logger.error("Location data missing latitude/longitude")
                return False
            
            # Ensure the location has a unique ID
            if 'id' not in location:
                location['id'] = str(uuid.uuid4())
            
            # Add timestamp if not present
            if not location.get('timestamp') and not location.get('datetime'):
                location['timestamp'] = datetime.datetime.now().isoformat()
            
            # Add to locations
            self.locations.append(location)
            
        else:
            # Handle Location object
            location_dict = {
                'latitude': getattr(location, 'latitude', 0),
                'longitude': getattr(location, 'longitude', 0),
                'datetime': getattr(location, 'datetime', None),
                'timestamp': getattr(location, 'datetime', None),
                'context': getattr(location, 'context', ""),
                'plugin': getattr(location, 'plugin', ""),
                'name': getattr(location, 'shortName', ""),
                'description': getattr(location, 'infowindow', ""),
                'visible': getattr(location, 'visible', True),
                'id': getattr(location, 'id', str(uuid.uuid4()))
            }
            self.locations.append(location_dict)
            
        # Update modified timestamp
        self.modified_at = datetime.datetime.now()
        self.dateEdited = self.modified_at
        return True
    
    def add_target(self, target):
        """Add a target to the project"""
        if target and target not in self.selectedTargets:
            self.selectedTargets.append(target)
            # Set primary target if not already set
            if not self.target:
                self.target = target
            return True
        return False
    
    def add_locations(self, locations):
        """Add multiple locations to the project"""
        for location in locations:
            self.add_location(location)
    
    def remove_location(self, location_id):
        """Remove a location by its ID"""
        for i, location in enumerate(self.locations):
            loc_id = None
            
            if isinstance(location, dict):
                loc_id = location.get('id')
            else:
                loc_id = getattr(location, 'id', None)
                
            if loc_id == location_id:
                del self.locations[i]
                self.modified_at = datetime.datetime.now()
                self.dateEdited = self.modified_at
                return True
        return False

    def to_dict(self):
        """Convert project to dictionary representation"""
        return {
            'name': self.name,
            'target': self.target,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'locations': self.locations,
            'metadata': self.metadata,
            'notes': self.notes or self.projectDescription,
            'tags': self.tags or self.projectKeywords,
            'settings': self.settings or self.viewSettings,
            'plugin_data': self.plugin_data,
            'selectedTargets': self.selectedTargets or ([self.target] if self.target else []),
            'analysis': self.metadata.get('analysis') or self.analysis,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create project from dictionary data"""
        project = cls(
            name=data['name'],
            target=data.get('target'),
            project_id=data.get('project_id')
        )
        
        # Parse timestamps
        if 'created_at' in data:
            try:
                if isinstance(data['created_at'], str):
                    project.created_at = datetime.datetime.fromisoformat(data['created_at'])
                elif isinstance(data['created_at'], (int, float)):
                    project.created_at = datetime.datetime.fromtimestamp(data['created_at'])
            except (ValueError, TypeError):
                logger.warning(f"Invalid created_at format: {data['created_at']}")
        
        if 'modified_at' in data:
            try:
                if isinstance(data['modified_at'], str):
                    project.modified_at = datetime.datetime.fromisoformat(data['modified_at'])
                elif isinstance(data['modified_at'], (int, float)):
                    project.modified_at = datetime.datetime.fromtimestamp(data['modified_at'])
            except (ValueError, TypeError):
                logger.warning(f"Invalid modified_at format: {data['modified_at']}")
        
        project.dateCreated = project.created_at
        project.dateEdited = project.modified_at
        
        project.locations = data.get('locations', [])
        project.metadata = data.get('metadata', {})
        project.notes = data.get('notes', '')
        project.projectDescription = project.notes
        project.tags = data.get('tags', [])
        project.projectKeywords = project.tags
        project.settings = data.get('settings', {})
        project.viewSettings = project.settings
        project.plugin_data = data.get('plugin_data', {})
        project.selectedTargets = data.get('selectedTargets', [])
        project.analysis = data.get('analysis')
        
        return project
    
    @classmethod
    def load(cls, path):
        """
        Load a project from file
        
        Args:
            path: Path to the project file
            
        Returns:
            Project instance or None if loading fails
        """
        try:
            project = cls()
            success = project.load(path)
            if success:
                return project
            return None
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return None
    
    def export_kml(self, path=None):
        """Export project locations to KML file"""
        if not path:
            if not self.path:
                logger.error("No project path specified for KML export")
                return None
            path = os.path.splitext(self.path)[0] + ".kml"
            
        try:
            # Look for KML template
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'config', 'app', 'kml_template.xml'
            )
            
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template = f.read()
            else:
                template = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <description>{description}</description>
    {placemarks}
  </Document>
</kml>'''
            
            # Generate placemarks
            placemarks = []
            for location in self.locations:
                if isinstance(location, dict):
                    lat = location.get('latitude')
                    lng = location.get('longitude')
                    name = location.get('name', 'Location')
                    desc = location.get('description', '')
                else:
                    lat = getattr(location, 'latitude', 0)
                    lng = getattr(location, 'longitude', 0)
                    name = getattr(location, 'shortName', 'Location')
                    desc = getattr(location, 'infowindow', '')
                    
                if lat and lng:
                    placemarks.append(f'''    <Placemark>
      <name>{name}</name>
      <description>{desc}</description>
      <Point>
        <coordinates>{lng},{lat}</coordinates>
      </Point>
    </Placemark>''')
            
            # Format and write KML
            kml_content = template.format(
                name=self.name,
                description=f"Project: {self.name}, Target: {self.target}",
                placemarks='\n'.join(placemarks)
            )
            
            with open(path, 'w') as f:
                f.write(kml_content)
                
            logger.info(f"Exported KML to {path}")
            return path
            
        except Exception as e:
            logger.error(f"Failed to export KML: {e}")
            return None
