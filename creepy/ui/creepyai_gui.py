#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from creepy.resources.icons import Icons
import creepy_resources_rc
import os
import logging
import datetime
import time
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QFileDialog, 
    QProgressDialog, QMenu, QAction, QLabel, QStatusBar,
    QToolBar, QDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QFont

# Import internal modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from creepy.models.Database import Database
from creepy.models.Location import Location
from creepy.models.Project import Project
from creepy.utilities.PluginManager import PluginManager
from creepy.utilities.WebScrapingUtility import WebScrapingUtility
from creepy.utilities.GeocodingUtility import GeocodingUtility
from creepy.utilities.ExportUtils import ExportManager

# Import UI components
from creepy.ui.PersonProjectWizard import PersonProjectWizard
from creepy.ui.PluginsConfig import PluginsConfigDialog
from creepy.ui.FilterLocationsDateDialog import FilterLocationsDateDialog
from creepy.ui.FilterLocationsPointDialog import FilterLocationsPointDialog
from creepy.ui.AboutDialog import AboutDialog
from creepy.ui.VerifyDeleteDialog import VerifyDeleteDialog
from creepy.ui.creepy_map_view import CreepyMapView

logger = logging.getLogger(__name__)

class CreepyMainWindow(QMainWindow):
    """Main window for the CreepyAI application."""
    
    def __init__(self, config_manager, parent=None):
        # Fix: Call the parent class constructor first
        super(CreepyMainWindow, self).__init__(parent)
        
        # Load icon styles
        try:
            style_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "resources", "styles", "icons.css")
            if os.path.exists(style_path):
                with open(style_path, 'r') as css_file:
                    self.setStyleSheet(css_file.read())
        except Exception as e:
            print(f"Failed to load icon styles: {e}")
    
        # Load icon styles
        try:
            style_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "resources", "styles", "icons.css")
            if os.path.exists(style_path):
                with open(style_path, 'r') as css_file:
                    self.setStyleSheet(css_file.read())
        except Exception as e:
            print(f"Failed to load icon styles: {e}")
    
        self.setWindowTitle("CreepyAI - Geolocation Intelligence")
        self.resize(1200, 800)
        
        # Initialize components
        self.config_manager = config_manager
        self.database = Database()
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.geocoder = GeocodingUtility(config_manager)
        self.export_manager = ExportManager()
        
        # Initialize recent projects list
        self.recent_projects = []
        self.load_recent_projects()
        
        # Set up UI components
        self._setup_ui()
        
        # Initialize data structures
        self.current_project = None
        self.current_target = None
        self.locations = []
        
        # Configure plugins with database and config
        self.plugin_manager.configure_plugins(config_manager, self.database)
        
        # Load settings
        self.load_settings()
        
        logger.info("Main window initialized")
        
        # Check for export dependencies
        QApplication.instance().processEvents()
        self.check_export_dependencies()
    
    def _setup_ui(self):
        """Set up the user interface."""
        try:
            # Set up central widget
            self.map_view = CreepyMapView(self)
            self.setCentralWidget(self.map_view)
            
            # Create toolbars
            self._create_toolbars()
            
            # Create status bar
            self.statusbar = QStatusBar()
            self.setStatusBar(self.statusbar)
            self.status_location_count = QLabel("No locations loaded")
            self.statusbar.addPermanentWidget(self.status_location_count)
            
            # Create menus
            self._create_menus()
        
        except Exception as e:
            logger.error(f"Failed to set up UI: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set up UI: {e}")
    
    def _create_toolbars(self):
        """Create application toolbars."""
        # Main toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setObjectName("MainToolbar")  # Fix: Set objectName for toolbar
        self.main_toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.TopToolBarArea, self.main_toolbar)
        
        # Project actions
        self.action_new_project = QAction(Icons.get_icon("new_project"), "New Project", self)
        self.action_new_project.triggered.connect(self.create_new_project)
        self.main_toolbar.addAction(self.action_new_project)
        
        self.action_open_project = QAction(Icons.get_icon("open_project"), "Open Project", self)
        self.action_open_project.triggered.connect(self.open_project)
        self.main_toolbar.addAction(self.action_open_project)
        
        self.action_save_project = QAction(Icons.get_icon("save_project"), "Save Project", self)
        self.action_save_project.triggered.connect(self.save_project)
        self.main_toolbar.addAction(self.action_save_project)
        
        self.main_toolbar.addSeparator()
        
        # Analysis actions
        self.action_analyze = QAction(Icons.get_icon("analyze"), "Analyze Data", self)
        self.action_analyze.triggered.connect(self.analyze_data)
        self.main_toolbar.addAction(self.action_analyze)
        
        self.action_export = QAction(Icons.get_icon("export"), "Export Data", self)
        self.action_export.triggered.connect(self.export_project)
        self.main_toolbar.addAction(self.action_export)
        
        self.main_toolbar.addSeparator()
        
        # Filter actions
        self.action_filter_date = QAction(Icons.get_icon("filter_date"), "Filter by Date", self)
        self.action_filter_date.triggered.connect(self.filter_by_date)
        self.main_toolbar.addAction(self.action_filter_date)
        
        self.action_filter_location = QAction(Icons.get_icon("filter_location"), "Filter by Location", self)
        self.action_filter_location.triggered.connect(self.filter_by_location)
        self.main_toolbar.addAction(self.action_filter_location)
        
        self.action_clear_filters = QAction(Icons.get_icon("clear_filters"), "Clear Filters", self)
        self.action_clear_filters.triggered.connect(self.clear_filters)
        self.main_toolbar.addAction(self.action_clear_filters)
    
    def _create_menus(self):
        """Create application menus."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        
        self.file_menu.addAction(self.action_new_project)
        self.file_menu.addAction(self.action_open_project)
        self.file_menu.addAction(self.action_save_project)
        
        self.file_menu.addSeparator()
        
        # Recent projects submenu
        self.recent_projects_menu = QMenu("Recent Projects", self)
        self.file_menu.addMenu(self.recent_projects_menu)
        self._update_recent_projects_menu()
        
        self.file_menu.addSeparator()
        
        # Export submenu
        self.export_menu = QMenu("Export", self)
        self.action_export_kml = QAction("Export to KML", self)
        self.action_export_kml.triggered.connect(lambda: self.export_project("kml"))
        self.export_menu.addAction(self.action_export_kml)
        
        self.action_export_csv = QAction("Export to CSV", self)
        self.action_export_csv.triggered.connect(lambda: self.export_project("csv"))
        self.export_menu.addAction(self.action_export_csv)
        
        self.action_export_html = QAction("Export to HTML Map", self)
        self.action_export_html.triggered.connect(lambda: self.export_project("html"))
        self.export_menu.addAction(self.action_export_html)
        
        self.action_export_json = QAction("Export to JSON", self)
        self.action_export_json.triggered.connect(lambda: self.export_project("json"))
        self.export_menu.addAction(self.action_export_json)
        
        self.file_menu.addMenu(self.export_menu)
        
        self.file_menu.addSeparator()
        
        # Exit action
        self.action_exit = QAction("E&xit", self)
        self.action_exit.triggered.connect(self.close)
        self.file_menu.addAction(self.action_exit)
        
        # Analysis menu
        self.analysis_menu = self.menuBar().addMenu("&Analysis")
        
        self.analysis_menu.addAction(self.action_analyze)
        
        self.analysis_menu.addSeparator()
        
        self.analysis_menu.addAction(self.action_filter_date)
        self.analysis_menu.addAction(self.action_filter_location)
        self.analysis_menu.addAction(self.action_clear_filters)
        
        # Tools menu
        self.tools_menu = self.menuBar().addMenu("&Tools")
        
        self.action_plugins_config = QAction("Plugin Configuration", self)
        self.action_plugins_config.triggered.connect(self.configure_plugins)
        self.tools_menu.addAction(self.action_plugins_config)
        
        self.action_settings = QAction("Settings", self)
        self.action_settings.triggered.connect(self.show_settings)
        self.tools_menu.addAction(self.action_settings)
    
    def create_new_project(self):
        """Create a new project."""
        wizard = PersonProjectWizard(self.plugin_manager)
        if wizard.exec_():
            project_data = wizard.get_project_data()
            self.current_project = Project(
                name=project_data.get('name', ''),
                description=project_data.get('description', ''),
                project_dir=project_data.get('directory', '')
            )
            for target in project_data.get('targets', []):
                self.current_project.add_target(target)
            self.save_project()
            self.update_project_ui()
            if project_data.get('analyze_now', False):
                self.analyze_data()
            self.statusbar.showMessage(f"Created new project: {self.current_project.name}")
    
    def open_project(self):
        """Open an existing project."""
        project_dir = QFileDialog.getExistingDirectory(self, "Open Project Directory")
        if not project_dir:
            return
        project_file = os.path.join(project_dir, 'project.json')
        if not os.path.exists(project_file):
            QMessageBox.warning(self, "Invalid Project", "The selected directory does not contain a valid CreepyAI project.")
            return
        self.current_project = Project.load(project_dir)
        if not self.current_project:
            QMessageBox.critical(self, "Project Error", "Failed to load the project. Please see the log for details.")
            return
        self.update_project_ui()
        self.statusbar.showMessage(f"Opened project: {self.current_project.name}")
    
    def save_project(self):
        """Save the current project."""
        if not self.current_project:
            return
        if not self.current_project.project_dir:
            project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory")
            if not project_dir:
                return
            self.current_project.set_project_dir(project_dir)
        if self.current_project.save():
            self.statusbar.showMessage(f"Project saved: {self.current_project.name}")
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save the project. Please see the log for details.")
    
    def update_project_ui(self):
        """Update UI with current project data."""
        if not self.current_project:
            self.statusbar.showMessage("No project loaded")
            return
        self.statusbar.showMessage(f"Project: {self.current_project.name}\nDescription: {self.current_project.description}\nLocations: {self.current_project.locations.count()}")
    
    def filter_by_date(self):
        """Show filter by date dialog."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to filter.")
            return
        dialog = FilterLocationsDateDialog(self.current_project, self)
        if dialog.exec_():
            self.statusbar.showMessage("Date filter applied")
    
    def filter_by_location(self):
        """Show filter by location point dialog."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to filter.")
            return
        dialog = FilterLocationsPointDialog(self.current_project, self)
        if dialog.exec_():
            self.statusbar.showMessage("Location filter applied")
    
    def clear_filters(self):
        """Clear all filters."""
        self.statusbar.showMessage("Filters cleared")
    
    def show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def analyze_data(self):
        """Perform analysis on the project data."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to analyze.")
            return
        QMessageBox.information(self, "Analysis", "Analysis feature not implemented yet.")
    
    def export_project(self, format="kml"):
        """Export project data."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to export.")
            return
        file_formats = {
            "kml": "KML Files (*.kml)",
            "csv": "CSV Files (*.csv)",
            "html": "HTML Files (*.html)",
            "json": "JSON Files (*.json)"
        }
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Project", f"{self.current_project.name}.{format}", file_formats[format])
        if not file_path:
            return
        success = self.export_manager.export_locations(self.current_project.locations, file_path, format)
        if success:
            self.statusbar.showMessage(f"Data exported to {file_path}")
        else:
            QMessageBox.critical(self, "Export Error", "Failed to export data. See log for details.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_project and self.current_project.is_modified():
            reply = QMessageBox.question(self, "Save Project", "The current project has unsaved changes. Save before closing?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save_project()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        self.save_settings()
        event.accept()
    
    def save_settings(self):
        """Save application settings."""
        settings = QSettings("CreepyAI", "CreepyAI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("recentProjects", self.recent_projects)
    
    def load_settings(self):
        """Load application settings."""
        settings = QSettings("CreepyAI", "CreepyAI")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
        self.recent_projects = settings.value("recentProjects", [])
    
    def check_export_dependencies(self):
        """Check for export-related dependencies and notify the user if any are missing."""
        missing_features = []
        try:
            import simplekml
        except ImportError:
            missing_features.append({'name': 'KML Export', 'package': 'simplekml', 'importance': 'optional'})
        if missing_features:
            feature_list = "\n".join([f"- {f['name']} (requires {f['package']})" for f in missing_features])
            QMessageBox.information(self, "Limited Functionality", f"Some features have limited functionality due to missing dependencies:\n\n{feature_list}\n\nYou can install these packages using:\npip install simplekml\n\nOr run the dependency installer:\npython core/install_dependencies.py --optional")
            for feature in missing_features:
                logger.warning(f"Missing dependency: {feature['package']} - {feature['name']} will be limited")

    def _update_recent_projects_menu(self):
        """Update the recent projects menu with recent project paths."""
        # Clear existing actions
        self.recent_projects_menu.clear()
        
        # If no recent projects, add disabled action
        if not self.recent_projects:
            action = QAction("No Recent Projects", self)
            action.setEnabled(False)
            self.recent_projects_menu.addAction(action)
            return
        
        # Add recent projects
        for project_path in self.recent_projects:
            if os.path.exists(project_path):
                project_name = os.path.basename(project_path)
                action = QAction(project_name, self)
                action.setData(project_path)
                action.triggered.connect(lambda checked, path=project_path: self.open_recent_project(path))
                self.recent_projects_menu.addAction(action)
        
        # Add separator and clear action
        if self.recent_projects:
            self.recent_projects_menu.addSeparator()
            clear_action = QAction("Clear Recent Projects", self)
            clear_action.triggered.connect(self.clear_recent_projects)
            self.recent_projects_menu.addAction(clear_action)

    def open_recent_project(self, project_path):
        """Open a project from the recent projects list."""
        if os.path.exists(project_path):
            self.current_project = Project.load(project_path)
            if self.current_project:
                # Update UI
                self.update_project_ui()
                # Add to recent projects (moves to top of list)
                self._add_to_recent_projects(project_path)
            else:
                # Remove from recent projects if it failed to load
                self._remove_from_recent_projects(project_path)
        else:
            # Remove from recent projects if it doesn't exist
            self._remove_from_recent_projects(project_path)
            QMessageBox.warning(self, "Project Not Found", f"The project at {project_path} no longer exists.")

    def _add_to_recent_projects(self, project_path):
        """Add a project to the recent projects list."""
        # Remove if already in the list
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        # Add to the beginning of the list
        self.recent_projects.insert(0, project_path)
        # Limit to 10 recent projects
        self.recent_projects = self.recent_projects[:10]
        # Update menu
        self._update_recent_projects_menu()

    def _remove_from_recent_projects(self, project_path):
        """Remove a project from the recent projects list."""
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
            # Update menu
            self._update_recent_projects_menu()

    def clear_recent_projects(self):
        """Clear the recent projects list."""
        self.recent_projects = []
        self._update_recent_projects_menu()

    def load_recent_projects(self):
        """Load recent projects from settings or config."""
        try:
            # Try to load from config manager if available
            if hasattr(self, 'config_manager') and self.config_manager:
                self.recent_projects = self.config_manager.get('recent_projects', [])
            else:
                self.recent_projects = []
        except Exception as e:
            logging.error(f"Failed to load recent projects: {e}")
            self.recent_projects = []

    def configure_plugins(self):
        """Open plugin configuration dialog"""
        try:
            from creepy.ui.PluginsConfig import PluginsConfigDialog
            config_dialog = PluginsConfigDialog(self.plugin_manager, parent=self)
            config_dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening plugin configuration: {str(e)}")
            QMessageBox.warning(self, "Plugin Configuration Error", 
                               f"Could not open plugin configuration: {str(e)}")

    def show_settings(self):
        """Open application settings dialog"""
        try:
            from creepy.ui.SettingsDialog import SettingsDialog
            settings_dialog = SettingsDialog(self.config_manager, parent=self)
            if settings_dialog.exec_():
                # Apply settings if needed
                self.statusbar.showMessage("Settings updated")
        except Exception as e:
            logger.error(f"Error opening settings: {str(e)}")
            QMessageBox.warning(self, "Settings Error", 
                               f"Could not open settings: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CreepyAIGUI(root)
    root.mainloop()