#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from app.resources.icons import Icons
import creepy.creepy_resources_rc as creepy_resources_rc
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
from app.models.Database import Database
from app.models.Location import Location
from app.models.Project import Project
from utilities.PluginManager import PluginManager
from utilities.WebScrapingUtility import WebScrapingUtility
from utilities.GeocodingUtility import GeocodingUtility
from utilities.ExportUtils import ExportManager

# Import UI components
from ui.PersonProjectWizard import PersonProjectWizard
from ui.PluginsConfig import PluginsConfigDialog
from ui.FilterLocationsDateDialog import FilterLocationsDateDialog
from ui.FilterLocationsPointDialog import FilterLocationsPointDialog
from ui.AboutDialog import AboutDialog
from ui.VerifyDeleteDialog import VerifyDeleteDialog
from ui.creepy_map_view import CreepyMapView

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
            from ui.PluginsConfig import PluginsConfigDialog
            config_dialog = PluginsConfigDialog(self.plugin_manager, parent=self)
            config_dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening plugin configuration: {str(e)}")
            QMessageBox.warning(self, "Plugin Configuration Error", 
                               f"Could not open plugin configuration: {str(e)}")

    def show_settings(self):
        """Open application settings dialog"""
        try:
            from ui.SettingsDialog import SettingsDialog
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

"""
Main GUI entry point for CreepyAI

This module initializes and launches the Qt GUI for CreepyAI.
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import Qt
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen, QMessageBox
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QPixmap
except ImportError:
    logging.error("PyQt5 not found. Please install it with: pip install PyQt5")
    sys.exit(1)

# Import CreepyAI modules
from app.gui.main.CreepyUI import Ui_MainWindow
from utilities.webengine_compat import setup_webengine_options
from app.core.logger import get_logger

logger = get_logger('creepyai.gui.launcher')

class CreepyAIMainWindow(QMainWindow):
    """Main window for CreepyAI application"""
    
    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app_instance = app_instance
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Set window title
        self.setWindowTitle(f"CreepyAI v{app_instance.config.get('app.version', '2.5.0')}")
        
        # Connect signals and slots
        self.setup_connections()
        
        # Initialize plugins
        self.plugin_widgets = {}
        self.load_plugins()
    
    def setup_connections(self):
        """Set up signal/slot connections"""
        # File menu
        if hasattr(self.ui, 'actionNew'):
            self.ui.actionNew.triggered.connect(self.new_project)
        if hasattr(self.ui, 'actionOpen'):
            self.ui.actionOpen.triggered.connect(self.open_project)
        if hasattr(self.ui, 'actionSave'):
            self.ui.actionSave.triggered.connect(self.save_project)
        if hasattr(self.ui, 'actionExit'):
            self.ui.actionExit.triggered.connect(self.close)
        
        # Plugins menu setup if exists
        if hasattr(self.ui, 'menuPlugins'):
            self.setup_plugins_menu()
    
    def setup_plugins_menu(self):
        """Set up the plugins menu with available plugins"""
        if not hasattr(self.ui, 'menuPlugins'):
            return
            
        self.ui.menuPlugins.clear()
        
        # Add actions for each plugin
        for plugin_name, plugin in self.app_instance.plugin_manager.active_plugins.items():
            action = self.ui.menuPlugins.addAction(plugin_name)
            action.triggered.connect(lambda checked, name=plugin_name: self.run_plugin(name))
    
    def load_plugins(self):
        """Load and initialize plugin UI components"""
        logger.info("Initializing plugin UI components")
        for plugin_name, plugin_info in self.app_instance.plugin_manager.active_plugins.items():
            plugin = plugin_info.get('instance')
            if not plugin:
                continue
                
            # If plugin has UI component, initialize it
            if hasattr(plugin, 'create_widget'):
                try:
                    widget = plugin.create_widget()
                    if widget:
                        self.plugin_widgets[plugin_name] = widget
                        logger.debug(f"Created UI widget for plugin {plugin_name}")
                except Exception as e:
                    logger.error(f"Error creating widget for plugin {plugin_name}: {e}")
    
    def run_plugin(self, plugin_name):
        """Run a specific plugin"""
        logger.info(f"Running plugin: {plugin_name}")
        plugin = self.app_instance.plugin_manager.get_plugin(plugin_name)
        if plugin:
            try:
                # Check if plugin has a GUI method
                if hasattr(plugin, 'run_gui'):
                    plugin.run_gui(self)
                else:
                    # Fall back to regular execute method
                    result = plugin.execute()
                    QMessageBox.information(self, f"Plugin {plugin_name}", 
                                           f"Plugin executed with result: {result}")
            except Exception as e:
                logger.error(f"Error running plugin {plugin_name}: {e}")
                QMessageBox.warning(self, "Plugin Error", 
                                    f"Error running plugin {plugin_name}: {str(e)}")
    
    def new_project(self):
        """Create a new project"""
        from app.gui.dialogs.PersonProjectWizard import PersonProjectWizard
        wizard = PersonProjectWizard(self)
        if wizard.exec_():
            # Get project data from wizard
            project_data = wizard.get_project_data()
            
            # Create new project
            project = self.app_instance.create_project(
                project_data.get('name', 'New Project'),
                project_data.get('target')
            )
            
            # Update UI
            self.update_project_ui(project)
            
            logger.info(f"Created new project: {project.name}")
    
    def open_project(self):
        """Open an existing project"""
        from PyQt5.QtWidgets import QFileDialog
        
        projects_dir = self.app_instance.config.get('app.projects_directory', 
                                                  os.path.join(project_root, 'projects'))
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", projects_dir, "Project Files (*.json)"
        )
        
        if file_path:
            try:
                project = self.app_instance.load_project(file_path)
                if project:
                    self.update_project_ui(project)
                    logger.info(f"Opened project: {project.name}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to load project")
            except Exception as e:
                logger.error(f"Error opening project: {e}")
                QMessageBox.warning(self, "Error", f"Failed to open project: {str(e)}")
    
    def save_project(self):
        """Save the current project"""
        project = self.app_instance.current_project
        if not project:
            QMessageBox.information(self, "No Project", "No project to save")
            return
            
        if project.path:
            project.save()
            logger.info(f"Saved project: {project.name}")
        else:
            from PyQt5.QtWidgets import QFileDialog
            
            projects_dir = self.app_instance.config.get('app.projects_directory', 
                                                      os.path.join(project_root, 'projects'))
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project", os.path.join(projects_dir, f"{project.name}.json"),
                "Project Files (*.json)"
            )
            
            if file_path:
                project.save(file_path)
                logger.info(f"Saved project to: {file_path}")
    
    def update_project_ui(self, project):
        """Update UI to reflect loaded project"""
        self.app_instance.current_project = project
        
        # Update window title
        self.setWindowTitle(f"CreepyAI - {project.name}")
        
        # Update any project-dependent UI elements
        if hasattr(self.ui, 'projectNameLabel'):
            self.ui.projectNameLabel.setText(project.name)
            
        # Update any maps or location displays
        self.update_locations_display()
    
    def update_locations_display(self):
        """Update the display of locations"""
        project = self.app_instance.current_project
        if not project:
            return
            
        # Update locations table if it exists
        if hasattr(self.ui, 'locationsTable'):
            self.update_locations_table(project.locations)
            
        # Update map if it exists
        if hasattr(self.ui, 'mapWidget'):
            self.update_map(project.locations)
    
    def update_locations_table(self, locations):
        """Update the locations table with project locations"""
        # Implementation depends on actual table widget being used
        pass
    
    def update_map(self, locations):
        """Update the map with project locations"""
        # Implementation depends on actual map widget being used
        pass

def show_splash_screen():
    """Show a splash screen while loading"""
    splash_path = os.path.join(project_root, 'assets', 'icons', 'ui', 'app_icon.png')
    
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        return splash
    
    return None

def launch_gui(app_instance):
    """
    Launch the CreepyAI GUI
    
    Args:
        app_instance: The CreepyAI application instance
    """
    try:
        # Configure web engine for maps
        setup_webengine_options()
        
        # Create Qt application if it doesn't exist
        qt_app = QApplication.instance()
        if not qt_app:
            qt_app = QApplication(sys.argv)
        
        # Show splash screen
        splash = show_splash_screen()
        
        # Create and show main window
        main_window = CreepyAIMainWindow(app_instance)
        main_window.show()
        
        # Close splash screen if it exists
        if splash:
            QTimer.singleShot(1000, splash.close)
        
        # Run the application
        sys.exit(qt_app.exec_())
        
    except Exception as e:
        logger.critical(f"Error launching GUI: {e}", exc_info=True)
        raise

"""
Simple CreepyAI GUI for testing.
"""
import os
import sys
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                           QPushButton, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt

# Add parent directory to path to allow importing
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Import UI modules
try:
    from app.gui.ui.about_dialog import AboutDialog
    from app.gui.ui.plugin_config_dialog import PluginsConfigDialog
    from app.gui.ui.settings_dialog import SettingsDialog
except ImportError as e:
    logging.warning(f"Could not import UI components: {e}")
    # Define minimal versions if import fails
    class AboutDialog:
        def __init__(self, parent=None):
            pass
        def exec_(self):
            return True
            
    class PluginsConfigDialog:
        def __init__(self, plugin_manager=None, parent=None):
            pass
        def exec_(self):
            return True
            
    class SettingsDialog:
        def __init__(self, config=None, parent=None):
            pass
        def exec_(self):
            return True

logger = logging.getLogger('creepyai.gui')

class CreepyAIGUI(QMainWindow):
    """Main window for CreepyAI application."""
    
    def __init__(self, engine=None):
        """Initialize the main window.
        
        Args:
            engine: CreepyAI engine instance
        """
        super().__init__()
        self.engine = engine
        self.setWindowTitle("CreepyAI")
        self.resize(800, 600)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Add welcome label
        self.welcome_label = QLabel("Welcome to CreepyAI!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.welcome_label)
        
        # Add version info
        version = engine.get_version() if engine else "2.5.0"
        self.version_label = QLabel(f"Version: {version}")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.version_label)
        
        # Add test button
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        self.layout.addWidget(self.test_button)
        
        # Add settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        self.layout.addWidget(self.settings_button)
        
        # Add plugins button
        self.plugins_button = QPushButton("Plugins")
        self.plugins_button.clicked.connect(self.show_plugins)
        self.layout.addWidget(self.plugins_button)
        
        # Create menus
        self.create_menus()
        
        logger.info("CreepyAI GUI initialized")
        
    def create_menus(self):
        """Create the application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        plugins_action = QAction("&Plugins", self)
        plugins_action.triggered.connect(self.show_plugins)
        tools_menu.addAction(plugins_action)
        
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def test_connection(self):
        """Test the connection to the engine."""
        if self.engine:
            status = self.engine.get_status()
            self.welcome_label.setText(f"Engine status: {status['initialized']}")
            logger.info(f"Engine status: {status}")
        else:
            self.welcome_label.setText("No engine connected")
            logger.warning("No engine connected")
            
    def show_plugins(self):
        """Show the plugins dialog."""
        if self.engine:
            plugin_count = len(self.engine.plugins)
            dialog = PluginsConfigDialog(self.engine.plugins, self)
            dialog.exec_()
            self.welcome_label.setText(f"Loaded plugins: {plugin_count}")
            logger.info(f"Loaded plugins: {plugin_count}")
        else:
            self.welcome_label.setText("No engine connected")
            logger.warning("No engine connected")
            
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.engine.config if self.engine else None, self)
        dialog.exec_()
            
    def show_about(self):
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec_()
        self.welcome_label.setText("CreepyAI - OSINT Platform")
        logger.info("About dialog shown")