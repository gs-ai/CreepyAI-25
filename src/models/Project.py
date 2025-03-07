#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shelve
import datetime
import logging
import shutil
import json
from models.Location import Location

logger = logging.getLogger(__name__)

class Project:
    """
    Represents a CreepyAI project with targets and locations.
    Projects are serialized using the shelve module.
    """
    
    def __init__(self, path=None):
        """
        Initialize a project object.
        
        Args:
            path: Path to the project file (.db) or None for new project
        """
        self.projectName = ""
        self.projectKeywords = []
        self.projectDescription = ""
        self.dateCreated = datetime.datetime.now()
        self.dateEdited = datetime.datetime.now()
        self.locations = []
        self.enabledPlugins = []
        self.viewSettings = {}
        self.selectedTargets = []
        self.analysis = None
        self.isAnalysisRunning = False
        
        # Load project if path is provided
        if path:
            self.load_project(path)
    
    def load_project(self, path):
        """
        Load a project from disk.
        
        Args:
            path: Path to the project file (.db)
        """
        try:
            # Remove .db extension if present
            if path.endswith('.db'):
                path = path[:-3]
                
            # Open the shelve database
            with shelve.open(path) as db:
                # Load basic project info
                self.projectName = db.get('projectName', "")
                self.projectKeywords = db.get('projectKeywords', [])
                self.projectDescription = db.get('projectDescription', "")
                self.dateCreated = db.get('dateCreated', datetime.datetime.now())
                self.dateEdited = db.get('dateEdited', datetime.datetime.now())
                
                # Load plugin and target configuration
                self.enabledPlugins = db.get('enabledPlugins', [])
                self.selectedTargets = db.get('selectedTargets', [])
                self.viewSettings = db.get('viewSettings', {})
                
                # Load locations with proper instantiation
                locations_data = db.get('locations', [])
                self.locations = []
                for loc_dict in locations_data:
                    # Convert the dict back to a Location object
                    location = Location()
                    location.latitude = loc_dict.get('latitude', 0)
                    location.longitude = loc_dict.get('longitude', 0)
                    location.datetime = loc_dict.get('datetime')
                    location.context = loc_dict.get('context', "")
                    location.plugin = loc_dict.get('plugin', "")
                    location.shortName = loc_dict.get('shortName', "")
                    location.infowindow = loc_dict.get('infowindow', "")
                    location.visible = loc_dict.get('visible', True)
                    location.id = loc_dict.get('id')
                    
                    self.locations.append(location)
                
                # Load analysis data if any
                self.analysis = db.get('analysis', None)
            
            logger.info(f"Project loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load project from {path}: {str(e)}")
            return False
    
    def storeProject(self, projectNode):
        """
        Store the project to disk.
        
        Args:
            projectNode: ProjectNode object containing the project
        """
        try:
            # Ensure projects directory exists
            projects_dir = os.path.join(os.getcwd(), 'projects')
            os.makedirs(projects_dir, exist_ok=True)
            
            project_path = os.path.join(projects_dir, self.projectName)
            
            # Update edit timestamp
            self.dateEdited = datetime.datetime.now()
            
            # Convert locations to serializable dictionaries
            locations_data = []
            for loc in self.locations:
                if isinstance(loc, Location):
                    # Convert Location object to dict
                    loc_dict = {
                        'latitude': loc.latitude,
                        'longitude': loc.longitude,
                        'datetime': loc.datetime,
                        'context': loc.context,
                        'plugin': loc.plugin,
                        'shortName': loc.shortName,
                        'infowindow': loc.infowindow,
                        'visible': loc.visible,
                        'id': loc.id
                    }
                    locations_data.append(loc_dict)
                else:
                    # If already a dict, use as is
                    locations_data.append(loc)
            
            # Store data in shelve database
            with shelve.open(project_path) as db:
                db['projectName'] = self.projectName
                db['projectKeywords'] = self.projectKeywords
                db['projectDescription'] = self.projectDescription
                db['dateCreated'] = self.dateCreated
                db['dateEdited'] = self.dateEdited
                db['enabledPlugins'] = self.enabledPlugins
                db['selectedTargets'] = self.selectedTargets
                db['locations'] = locations_data
                db['viewSettings'] = self.viewSettings
                db['analysis'] = self.analysis
            
            logger.info(f"Project saved to {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project: {str(e)}")
            return False
    
    def deleteProject(self, project_file):
        """
        Delete a project from disk.
        
        Args:
            project_file: Project filename (with .db extension)
        """
        try:
            projects_dir = os.path.join(os.getcwd(), 'projects')
            project_path = os.path.join(projects_dir, project_file)
            
            # Remove the shelve database files
            base_path = project_path[:-3]  # Remove .db extension
            for ext in ['', '.db', '.dat', '.bak', '.dir']:
                if os.path.exists(base_path + ext):
                    os.remove(base_path + ext)
            
            logger.info(f"Project deleted: {project_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_file}: {str(e)}")
            return False
    
    @staticmethod
    def getProjectsList():
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
            for filename in os.listdir(projects_dir):
                # Check for shelve database files
                if filename.endswith('.db'):
                    project_name = filename[:-3]  # Remove .db extension
                    project_path = os.path.join(projects_dir, project_name)
                    
                    # Get basic info from shelve
                    try:
                        with shelve.open(project_path) as db:
                            projects.append({
                                'name': db.get('projectName', project_name),
                                'date': db.get('dateEdited', datetime.datetime.now()),
                                'path': project_path
                            })
                    except Exception:
                        # Include the project even if we can't read its details
                        projects.append({
                            'name': project_name,
                            'date': datetime.datetime.now(),
                            'path': project_path
                        })
            
            # Sort projects by date
            projects.sort(key=lambda x: x['date'], reverse=True)
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects list: {str(e)}")
            return []
