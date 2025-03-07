import logging
from typing import List, Optional
from .settings_manager import SettingsManager

class CreepyMainWindow:
    def __init__(self, settings_manager=None, *args, **kwargs):
        # ...existing code...
        
        # Initialize settings manager
        self.settings_manager = settings_manager or SettingsManager()
        
        # Initialize recent projects list
        self.recent_projects = []
        self.load_recent_projects()
        
        # ...existing code...
    
    def setup_ui(self):
        # ...existing code...
    
    def load_recent_projects(self):
        """Load recent projects from settings."""
        try:
            self.recent_projects = self.settings_manager.get_recent_projects()
            logging.debug(f"Loaded {len(self.recent_projects)} recent projects")
        except Exception as e:
            logging.error(f"Failed to load recent projects: {e}")
            self.recent_projects = []
            self.show_error_message("Recent Projects", 
                                   "Could not load your recent projects. The list has been reset.")
    
    def add_recent_project(self, project_path: str):
        """Add a project to the recent projects list and save to settings."""
        try:
            self.settings_manager.add_recent_project(project_path)
            self.recent_projects = self.settings_manager.get_recent_projects()
            self.update_recent_projects_menu()
            logging.debug(f"Added {project_path} to recent projects")
        except Exception as e:
            logging.error(f"Failed to add recent project: {e}")
            self.show_error_message("Recent Projects", 
                                   "Could not update recent projects list.")
    
    def update_recent_projects_menu(self):
        """Update the recent projects menu with current list."""
        # Implementation depends on your UI framework
        # This is a placeholder for the actual implementation
        pass
    
    def show_error_message(self, title: str, message: str):
        """Display a user-friendly error message."""
        # Implementation depends on your UI framework
        # For example with PyQt:
        # QMessageBox.warning(self, title, message)
        
        # Fallback to console if UI not available
        logging.warning(f"{title}: {message}")