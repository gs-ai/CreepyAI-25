#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
import datetime
import shutil
from pathlib import Path

from .LocationsList import LocationsList

logger = logging.getLogger(__name__)

class Project:
    """
    Class representing a CreepyAI project.
    Manages targets, locations, and project metadata.
    """
    
    def __init__(self, name="", description="", project_dir=None):
        """Initialize a new project."""
        self.name = name
        self.description = description
        self.project_dir = project_dir
        self.targets = []
        self.metadata = {
            "created": datetime.datetime.now().isoformat(),
            "modified": datetime.datetime.now().isoformat(),
            "version": "1.0"
        }
        self.locations = LocationsList()
        self.analysis_results = {}
        self._modified = False
    
    def add_target(self, target_data):
        """
        Add a target to the project.
        
        Args:
            target_data: Dictionary containing target information
        
        Returns:
            bool: True if target was added successfully
        """
        if not isinstance(target_data, dict):
            logger.error("Target data must be a dictionary")
            return False
        
        # Ensure required fields
        if "name" not in target_data:
            target_data["name"] = "Unknown"
        
        # Add to targets list
        self.targets.append(target_data)
        self._modified = True
        return True
    
    def remove_target(self, target_index):
        """
        Remove a target from the project.
        
        Args:
            target_index: Index of the target to remove
            
        Returns:
            bool: True if target was removed successfully
        """
        if 0 <= target_index < len(self.targets):
            del self.targets[target_index]
            self._modified = True
            return True
        return False
    
    def update_target(self, target_index, target_data):
        """
        Update a target's information.
        
        Args:
            target_index: Index of the target to update
            target_data: New target data
            
        Returns:
            bool: True if target was updated successfully
        """
        if 0 <= target_index < len(self.targets):
            self.targets[target_index].update(target_data)
            self._modified = True
            return True
        return False
    
    def add_locations(self, locations, target_index=None):
        """
        Add locations to the project, optionally associating them with a target.
        
        Args:
            locations: List of Location objects
            target_index: Optional target index to associate with
            
        Returns:
            int: Number of locations added
        """
        added_count = 0
        
        # If target specified, add target_id to locations
        if target_index is not None and 0 <= target_index < len(self.targets):
            target_name = self.targets[target_index].get("name", "Unknown")
            
            for location in locations:
                # Add target info to location context
                if not hasattr(location, "context") or location.context is None:
                    location.context = {}
                
                location.context["target"] = target_name
                location.target_id = target_index
                
                if self.locations.add_location(location):
                    added_count += 1
        else:
            # Just add the locations without target association
            for location in locations:
                if self.locations.add_location(location):
                    added_count += 1
        
        if added_count > 0:
            self._modified = True
            self.metadata["modified"] = datetime.datetime.now().isoformat()
            
        return added_count
    
    def save(self, project_dir=None):
        """
        Save the project to disk.
        
        Args:
            project_dir: Directory to save to (uses self.project_dir if None)
            
        Returns:
            bool: True if successful
        """
        if project_dir:
            self.project_dir = project_dir
        
        if not self.project_dir:
            logger.error("No project directory specified")
            return False
        
        try:
            # Ensure directory exists
            os.makedirs(self.project_dir, exist_ok=True)
            
            # Create project.json file
            project_data = {
                "name": self.name,
                "description": self.description,
                "metadata": self.metadata,
                "targets": self.targets
            }
            
            with open(os.path.join(self.project_dir, "project.json"), "w") as f:
                json.dump(project_data, f, indent=2)
            
            # Save locations
            locations_file = os.path.join(self.project_dir, "locations.json")
            self.locations.to_json(locations_file)
            
            # Save analysis results if any
            if self.analysis_results:
                analysis_file = os.path.join(self.project_dir, "analysis.json")
                with open(analysis_file, "w") as f:
                    json.dump(self.analysis_results, f, indent=2)
            
            self._modified = False
            logger.info(f"Project saved to {self.project_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project: {str(e)}")
            return False
    
    @classmethod
    def load(cls, project_dir):
        """
        Load a project from disk.
        
        Args:
            project_dir: Directory containing the project files
            
        Returns:
            Project: Loaded project or None if loading failed
        """
        try:
            # Check if project.json exists
            project_file = os.path.join(project_dir, "project.json")
            if not os.path.exists(project_file):
                logger.error(f"Project file not found: {project_file}")
                return None
            
            # Load project data
            with open(project_file, "r") as f:
                project_data = json.load(f)
            
            # Create project object
            project = cls(
                name=project_data.get("name", ""),
                description=project_data.get("description", ""),
                project_dir=project_dir
            )
            
            # Set metadata
            project.metadata = project_data.get("metadata", {})
            
            # Load targets
            project.targets = project_data.get("targets", [])
            
            # Load locations if available
            locations_file = os.path.join(project_dir, "locations.json")
            if os.path.exists(locations_file):
                project.locations = LocationsList.from_json(file_path=locations_file)
            
            # Load analysis results if available
            analysis_file = os.path.join(project_dir, "analysis.json")
            if os.path.exists(analysis_file):
                with open(analysis_file, "r") as f:
                    project.analysis_results = json.load(f)
            
            project._modified = False
            logger.info(f"Project loaded from {project_dir}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to load project: {str(e)}")
            return None
    
    def is_modified(self):
        """Check if the project has been modified since last save."""
        return self._modified
    
    def export(self, export_dir, format_types=None):
        """
        Export project data to various formats.
        
        Args:
            export_dir: Directory to export to
            format_types: List of formats to export (kml, csv, html, json)
            
        Returns:
            dict: Dictionary of export results by format
        """
        if not format_types:
            format_types = ["kml", "csv", "html", "json"]
        
        # Create export directory
        os.makedirs(export_dir, exist_ok=True)
        
        results = {}
        
        # Get the export utilities
        from ..utilities.ExportUtils import ExportManager
        export_manager = ExportManager()
        
        # Export to each requested format
        for format_type in format_types:
            file_path = os.path.join(export_dir, f"{self.name}_{datetime.datetime.now().strftime('%Y%m%d')}.{format_type}")
            success = export_manager.export_locations(self.locations, file_path, format_type)
            results[format_type] = {
                "path": file_path,
                "success": success
            }
        
        return results
    
    def __str__(self):
        """String representation of the project."""
        return f"Project: {self.name} ({len(self.targets)} targets, {self.locations.count()} locations)"