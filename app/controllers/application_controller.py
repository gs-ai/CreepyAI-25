"""
Application Controller for CreepyAI
Manages application state, startup/shutdown procedures, and component coordination
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox

from app.gui.ui.main.main_window import MainWindow
from app.models.project import Project

logger = logging.getLogger(__name__)

class ApplicationController:
    """Controller for managing the CreepyAI application"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        self.current_project = None
    
    def start(self):
        """Start the application"""
        self.main_window.show()
        sys.exit(self.app.exec_())
    
    def new_project(self):
        """Create a new project"""
        self.current_project = Project()
        self.main_window.set_project(self.current_project)
        logger.info("New project created")
    
    def open_project(self, path: str):
        """Open an existing project"""
        project = Project.load(path)
        if project:
            self.current_project = project
            self.main_window.set_project(self.current_project)
            logger.info(f"Project loaded from {path}")
        else:
            QMessageBox.critical(self.main_window, "Error", f"Failed to load project from {path}")
    
    def save_project(self, path: Optional[str] = None):
        """Save the current project"""
        if not self.current_project:
            QMessageBox.warning(self.main_window, "No Project", "There is no project to save.")
            return
        
        if self.current_project.save(path):
            QMessageBox.information(self.main_window, "Project Saved", "Project saved successfully.")
            logger.info(f"Project saved to {path or self.current_project.path}")
        else:
            QMessageBox.critical(self.main_window, "Error", "Failed to save project.")
    
    def import_data(self):
        """Import data into the current project"""
        if not self.current_project:
            QMessageBox.warning(self.main_window, "No Project", "There is no project to import data into.")
            return
        
        # Implementation for importing data
        pass
    
    def export_data(self):
        """Export data from the current project"""
        if not self.current_project:
            QMessageBox.warning(self.main_window, "No Project", "There is no project to export data from.")
            return
        
        # Implementation for exporting data
        pass
    
    def manage_plugins(self):
        """Manage plugins"""
        # Implementation for managing plugins
        pass
