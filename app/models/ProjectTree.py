"""
ProjectTree model for CreepyAI.
Provides a tree structure for projects.
"""
import os
import json
from typing import Dict, List, Any, Optional


class ProjectTree:
    """Represents a tree structure of projects."""
    
    def __init__(self):
        """Initialize the project tree."""
        self.projects = {}
        self.root_projects = []
        self.project_relationships = {}  # parent_id -> [child_ids]
    
    def add_project(self, project, parent_id=None):
        """
        Add a project to the tree.
        
        Args:
            project: Project object to add
            parent_id: Optional parent project ID
        """
        project_id = project.id
        self.projects[project_id] = project
        
        if parent_id:
            if parent_id not in self.project_relationships:
                self.project_relationships[parent_id] = []
            self.project_relationships[parent_id].append(project_id)
        else:
            self.root_projects.append(project_id)
    
    def get_project(self, project_id):
        """
        Get a project by ID.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Project object or None if not found
        """
        return self.projects.get(project_id)
    
    def get_child_projects(self, project_id):
        """
        Get child projects of a project.
        
        Args:
            project_id: ID of the parent project
            
        Returns:
            List of child Project objects
        """
        child_ids = self.project_relationships.get(project_id, [])
        return [self.projects[child_id] for child_id in child_ids if child_id in self.projects]
    
    def get_root_projects(self):
        """
        Get root projects (those without parents).
        
        Returns:
            List of root Project objects
        """
        return [self.projects[project_id] for project_id in self.root_projects if project_id in self.projects]
    
    def remove_project(self, project_id):
        """
        Remove a project from the tree.
        
        Args:
            project_id: ID of the project to remove
            
        Returns:
            True if successful, False otherwise
        """
        if project_id not in self.projects:
            return False
        
        # Remove from root projects if present
        if project_id in self.root_projects:
            self.root_projects.remove(project_id)
        
        # Remove from parent's children
        for parent_id, children in self.project_relationships.items():
            if project_id in children:
                children.remove(project_id)
        
        # Remove project's children relationships
        if project_id in self.project_relationships:
            del self.project_relationships[project_id]
        
        # Remove project
        del self.projects[project_id]
        return True
    
    def to_dict(self):
        """
        Convert the tree to a dictionary.
        
        Returns:
            Dictionary representation of the tree
        """
        projects_dict = {}
        for project_id, project in self.projects.items():
            projects_dict[project_id] = project.to_dict()
        
        return {
            'projects': projects_dict,
            'root_projects': self.root_projects,
            'relationships': self.project_relationships
        }
    
    def to_json(self):
        """
        Convert the tree to a JSON string.
        
        Returns:
            JSON string representation of the tree
        """
        return json.dumps(self.to_dict())
