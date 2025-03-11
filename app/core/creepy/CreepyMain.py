#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import datetime
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root directory to Python path to ensure imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QMessageBox, 
    QFileDialog, QInputDialog, QWidget, QListWidgetItem, 
    QSplitter, QTabWidget
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QIcon

# Try multiple import paths for UI file
try:
    from app.gui.ui.creepyai_mainwindow_ui import Ui_CreepyAIMainWindow
except ImportError as e:
    logging.error(f"Could not import UI using standard path: {e}")
    try:
        # Try relative import as fallback
        sys.path.insert(0, os.path.join(project_root, "app", "gui", "ui"))
        from creepyai_mainwindow_ui import Ui_CreepyAIMainWindow
    except ImportError as e:
        logging.critical(f"Failed to import UI: {e}. Please check that the UI file exists.")
        sys.exit(1)

# Import map view
try:
    from app.gui.map_view import MapView
except ImportError as e:
    logging.error(f"Could not import MapView: {e}")
    MapView = None

# Import plugin manager
try:
    from app.core.plugins import PluginManager
except ImportError as e:
    logging.error(f"Could not import PluginManager: {e}")
    PluginManager = None

# Setup logging
log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'creepy_main.log')

logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add console handler for better debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(console_handler)

# Ensure Qt paths are correct
def setup_qt_paths():
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        qt_lib_path = os.path.join(conda_prefix, 'lib')
        qt_plugin_path = os.path.join(conda_prefix, 'lib/qt/plugins')

        os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
        os.environ['DYLD_FRAMEWORK_PATH'] = qt_lib_path
        os.environ.pop('DYLD_LIBRARY_PATH', None)

        sys.path.insert(0, qt_lib_path)
        logger.info(f"Qt paths set up. Plugin path: {qt_plugin_path}")
        return True
    return False

# Initialize Qt paths
if not setup_qt_paths():
    logger.warning("Could not set up Qt paths automatically. Using default environment paths.")

# Define Main Window Class
class CreepyAIMain(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing CreepyAI Main Window...")
        try:
            # Initialize data structures
            self.current_project = None
            self.current_locations = []
            self.settings = {}
            
            # Set up the UI
            self.ui = Ui_CreepyAIMainWindow()
            self.ui.setupUi(self)
            self.setWindowTitle("CreepyAI - Geolocation OSINT AI Tool")
            
            # Initialize the map view
            self.setup_map_view()
            
            # Initialize plugins
            self.setup_plugins()
            
            # Connect UI signals
            self.connect_signals()
            
            # Set up project directory
            self.project_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "projects")
            os.makedirs(self.project_dir, exist_ok=True)
            
            # Load settings
            self.load_settings()
            
            # Apply icons to UI
            self.apply_icons()
            
            logger.info("CreepyAI Main Window initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing UI: {e}", exc_info=True)
            raise
            
    def setup_map_view(self):
        """Initialize and set up the map view"""
        if MapView is None:
            logger.error("MapView class not available. Map functionality will be disabled.")
            return False
            
        try:
            # Create the map view
            self.map_view = MapView(self)
            
            # Add it to the map container
            layout = QVBoxLayout(self.ui.mapContainer)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.map_view)
            
            # Load the map
            self.map_view.mapLoaded.connect(self.on_map_loaded)
            self.map_view.locationClicked.connect(self.on_map_location_clicked)
            
            # Load the Leaflet map
            self.map_view.load_leaflet_map()
            
            logger.info("Map view set up successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up map view: {e}", exc_info=True)
            return False
            
    def setup_plugins(self):
        """Initialize and load plugins"""
        if PluginManager is None:
            logger.error("PluginManager class not available. Plugin functionality will be disabled.")
            return False
            
        try:
            # Create plugin manager
            self.plugin_manager = PluginManager()
            
            # Discover available plugins
            self.plugin_manager.discover_plugins()
            
            # Try to use the advanced plugin browser if available
            try:
                from app.gui.plugin_browser import PluginBrowserWidget
                
                # Check if we have a plugins tab
                if hasattr(self.ui, 'pluginsTab') and self.ui.pluginsTab:
                    # Create layout if it doesn't exist
                    if not self.ui.pluginsTab.layout():
                        self.ui.pluginsTab.setLayout(QVBoxLayout())
                    
                    # Remove existing widgets
                    while self.ui.pluginsTab.layout().count():
                        item = self.ui.pluginsTab.layout().takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    
                    # Create and add the plugin browser
                    self.plugin_browser = PluginBrowserWidget(self.ui.pluginsTab)
                    self.ui.pluginsTab.layout().addWidget(self.plugin_browser)
                    
                    # Set the plugin manager in the browser
                    self.plugin_browser.set_plugin_manager(self.plugin_manager)
                    
                    # Connect signals
                    self.plugin_browser.pluginRun.connect(self.on_run_plugin)
                    self.plugin_browser.pluginConfigure.connect(self.on_configure_plugin)
                    
                    logger.info("Advanced plugin browser initialized successfully")
                    return True
                else:
                    logger.warning("Plugins tab not found, falling back to simple plugin list")
            except ImportError:
                logger.warning("Could not import PluginBrowserWidget, using simple plugin list")
            except Exception as e:
                logger.error(f"Error setting up plugin browser: {e}", exc_info=True)
                
            # Fall back to simple plugin list
            self.populate_plugin_list()
            
            logger.info("Plugin system initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing plugin system: {e}", exc_info=True)
            return False
            
    def populate_plugin_list(self):
        """Populate the plugin list widget with available plugins"""
        try:
            self.ui.pluginListWidget.clear()
            
            plugins = self.plugin_manager.get_all_plugins()
            
            # Group plugins by category
            by_category = {}
            for name, plugin in plugins.items():
                category = self.plugin_manager.get_category(name)
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append((name, plugin))
            
            # Add plugins by category
            for category in sorted(by_category.keys()):
                # Add category header item
                category_item = QListWidgetItem(f"== {category.upper()} ==")
                category_item.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable
                font = category_item.font()
                font.setBold(True)
                category_item.setFont(font)
                self.ui.pluginListWidget.addItem(category_item)
                
                # Add plugins in this category
                for name, plugin in sorted(by_category[category]):
                    # Create list widget item
                    item = QListWidgetItem(f"  {name}")
                    item.setData(Qt.UserRole, name)  # Store actual plugin name
                    
                    # Add plugin info as tooltip
                    if hasattr(plugin, 'get_info'):
                        info = plugin.get_info()
                        tooltip = f"{info.get('name', name)} v{info.get('version', '1.0')}\n"
                        tooltip += f"Category: {category}\n"
                        tooltip += f"Author: {info.get('author', 'Unknown')}\n"
                        tooltip += f"Description: {info.get('description', 'No description')}"
                        item.setToolTip(tooltip)
                    
                    # Add to list widget
                    self.ui.pluginListWidget.addItem(item)
                
            # Enable or disable buttons based on selection
            self.update_plugin_buttons()
            
            logger.info(f"Loaded {len(plugins)} plugins across {len(by_category)} categories")
            return True
        except Exception as e:
            logger.error(f"Error populating plugin list: {e}", exc_info=True)
            return False
    
    def connect_signals(self):
        """Connect UI signals to their handlers"""
        try:
            # File menu - check if each action exists before connecting
            if hasattr(self.ui, 'actionNew'):
                self.ui.actionNew.triggered.connect(self.on_new_project)
            if hasattr(self.ui, 'actionOpen'):
                self.ui.actionOpen.triggered.connect(self.on_open_project)
            if hasattr(self.ui, 'actionSave'):
                self.ui.actionSave.triggered.connect(self.on_save_project)
            if hasattr(self.ui, 'actionImport'):
                self.ui.actionImport.triggered.connect(self.on_import_locations)
            if hasattr(self.ui, 'actionExport'):
                self.ui.actionExport.triggered.connect(self.on_export_locations)
            if hasattr(self.ui, 'actionExit'):
                self.ui.actionExit.triggered.connect(self.close)
            
            # Tools menu
            if hasattr(self.ui, 'actionPluginManager'):
                self.ui.actionPluginManager.triggered.connect(self.on_manage_plugins)
            if hasattr(self.ui, 'actionSettings'):
                self.ui.actionSettings.triggered.connect(self.on_settings)
            
            # Plugin actions
            if hasattr(self.ui, 'runPluginButton'):
                self.ui.runPluginButton.clicked.connect(self.on_run_plugin_clicked)
            if hasattr(self.ui, 'configPluginButton'):
                self.ui.configPluginButton.clicked.connect(self.on_configure_plugin_clicked)
                
            logger.debug("UI signals connected successfully")
            
        except Exception as e:
            logger.error(f"Error connecting signals: {e}")

    def update_plugin_buttons(self):
        """Enable or disable plugin buttons based on selection"""
        selected_items = self.ui.pluginListWidget.selectedItems()
        
        # Only enable buttons if a plugin (not category header) is selected
        has_plugin_selection = any(item.data(Qt.UserRole) is not None for item in selected_items)
        
        self.ui.runPluginButton.setEnabled(has_plugin_selection)
        self.ui.configPluginButton.setEnabled(has_plugin_selection)
        
    # Slot methods for UI signals
    def on_map_loaded(self, success):
        """Called when the map has finished loading"""
        if success:
            logger.info("Map loaded successfully")
            # Center map on a default location (e.g., San Francisco)
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.center_map(37.7749, -122.4194, 12)
        else:
            logger.error("Failed to load map")
            
    def on_map_location_clicked(self, lat, lon, info):
        """Called when a location on the map is clicked"""
        logger.info(f"Map clicked at {lat}, {lon}")
        
    def on_run_plugin_clicked(self):
        """Run the selected plugin"""
        selected_items = self.ui.pluginListWidget.selectedItems()
        if not selected_items:
            return
            
        # Get the actual plugin name from the user role data
        plugin_name = selected_items[0].data(Qt.UserRole)
        if not plugin_name:
            return  # It's a category header, not a plugin
            
        logger.info(f"Running plugin: {plugin_name}")
        
        # Get plugin category to determine plugin type
        category = self.plugin_manager.get_category(plugin_name)
        
        # For OSM Search plugin, prompt for search query
        if plugin_name == "osm_search" or "search" in plugin_name.lower():
            query, ok = QInputDialog.getText(
                self, "OSM Search", "Enter location to search:"
            )
            if ok and query:
                try:
                    results = self.plugin_manager.run_plugin(plugin_name, query)
                    self._display_plugin_locations(results, f"{plugin_name}: {query}")
                except Exception as e:
                    logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                    QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")
        
        # For EXIF extraction or file-based plugins
        elif plugin_name == "exif_extractor" or category == "data_extraction":
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "", 
                "Image Files (*.jpg *.jpeg *.png *.gif);;All Files (*)"
            )
            if files:
                try:
                    results = self.plugin_manager.run_plugin(plugin_name, files)
                    self._display_plugin_locations(results, f"{plugin_name}: {len(files)} files")
                except Exception as e:
                    logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                    QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")
        else:
            # Generic plugin run
            try:
                result = self.plugin_manager.run_plugin(plugin_name)
                if isinstance(result, list) and len(result) > 0 and all(isinstance(item, dict) for item in result):
                    self._display_plugin_locations(result)
                else:
                    QMessageBox.information(self, "Plugin Result", "Plugin executed successfully.")
            except Exception as e:
                logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")

    def on_run_plugin(self, plugin_name):
        """Run a plugin by name (called from plugin browser)"""
        logger.info(f"Running plugin: {plugin_name}")
        
        # Get category to determine plugin type
        category = self.plugin_manager.get_category(plugin_name)
        
        # Location search plugins
        if plugin_name == "osm_search" or "search" in plugin_name.lower() or category == "location_services":
            query, ok = QInputDialog.getText(
                self, f"Run {plugin_name}", "Enter location or search term:"
            )
            if ok and query:
                try:
                    results = self.plugin_manager.run_plugin(plugin_name, query)
                    self._display_plugin_locations(results, f"{plugin_name}: {query}")
                except Exception as e:
                    logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                    QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")
        
        # Data extraction plugins
        elif plugin_name == "exif_extractor" or category == "data_extraction":
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "", 
                "Image Files (*.jpg *.jpeg *.png *.gif);;All Files (*)"
            )
            if files:
                try:
                    results = self.plugin_manager.run_plugin(plugin_name, files)
                    self._display_plugin_locations(results, f"{plugin_name}: {len(files)} files")
                except Exception as e:
                    logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                    QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")
        
        # Social media plugins
        elif category == "social_media":
            username, ok = QInputDialog.getText(
                self, f"Run {plugin_name}", "Enter username:"
            )
            if ok and username:
                try:
                    results = self.plugin_manager.run_plugin(plugin_name, username)
                    self._display_plugin_locations(results, f"{plugin_name}: {username}")
                except Exception as e:
                    logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                    QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")
        
        # Generic plugin
        else:
            try:
                results = self.plugin_manager.run_plugin(plugin_name)
                
                # Check if results could be location data
                if isinstance(results, list) and results:
                    self._display_plugin_locations(results)
                else:
                    QMessageBox.information(self, "Plugin Result", "Plugin executed successfully.")
            except Exception as e:
                logger.error(f"Error running plugin {plugin_name}: {e}", exc_info=True)
                QMessageBox.warning(self, "Plugin Error", f"Error running plugin: {str(e)}")

    def _display_plugin_locations(self, locations, title="Plugin Results"):
        """Display location results from a plugin on the map and in the analysis view"""
        if not locations:
            QMessageBox.information(self, title, "No location data found.")
            return

        # Standardize locations first
        try:
            from app.core.plugins.standardize import LocationStandardizer
            locations = LocationStandardizer.standardize_locations(locations)
        except ImportError:
            # Continue with original locations if standardizer not available
            pass
        
        # Store the locations
        self.current_locations = locations
        
        # Clear previous results
        if hasattr(self, 'map_view') and self.map_view:
            self.map_view.clear_markers()
        
        # Clear analysis text
        if hasattr(self.ui, 'analysisTextBrowser'):
            self.ui.analysisTextBrowser.clear()
            self.ui.analysisTextBrowser.append(f"<h2>{title}</h2>")
        
        # Add each location to the map and analysis view
        for i, location in enumerate(locations):
            # Skip if missing lat/lon
            if 'lat' not in location or 'lon' not in location:
                continue
                
            lat = float(location['lat'])
            lon = float(location['lon'])
            name = location.get('name', f"Location {i+1}")
            
            # Build info string for popup
            info_parts = []
            exclude_keys = ['lat', 'lon', 'latitude', 'longitude', 'name', 'title']
            
            for key, value in location.items():
                if key not in exclude_keys and not key.startswith('_'):
                    # Skip complex nested objects
                    if isinstance(value, dict) or isinstance(value, list):
                        continue
                    info_parts.append(f"{key}: {value}")
            
            info = "<br>".join(info_parts)
            
            # Add to map
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.add_marker(lat, lon, name, info)
            
            # Add to analysis view
            if hasattr(self.ui, 'analysisTextBrowser'):
                self.ui.analysisTextBrowser.append(f"<p><b>{name}</b><br>")
                self.ui.analysisTextBrowser.append(f"Coordinates: {lat}, {lon}<br>")
                for part in info_parts[:5]:  # Limit to first 5 properties
                    self.ui.analysisTextBrowser.append(f"{part}<br>")
                if len(info_parts) > 5:
                    self.ui.analysisTextBrowser.append("(more properties available)...")
                self.ui.analysisTextBrowser.append("</p>")
        
        # Center map on first result
        if locations and hasattr(self, 'map_view') and self.map_view:
            first_loc = locations[0]
            lat = float(first_loc['lat'])
            lon = float(first_loc['lon'])
            self.map_view.center_map(lat, lon, 12)
        
        # Switch to appropriate tab
        if hasattr(self.ui, 'rightTabWidget'):
            # Find the analysis tab - it might be named differently
            for i in range(self.ui.rightTabWidget.count()):
                tab_name = self.ui.rightTabWidget.tabText(i).lower()
                if 'analysis' in tab_name or 'result' in tab_name:
                    self.ui.rightTabWidget.setCurrentIndex(i)
                    break

    def on_configure_plugin(self, plugin_name):
        """Configure a plugin by name (called from plugin browser)"""
        logger.info(f"Configuring plugin: {plugin_name}")
        
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin and hasattr(plugin, 'configure'):
            try:
                result = plugin.configure()
                if result:
                    QMessageBox.information(self, "Plugin Configuration", 
                                           f"Plugin '{plugin_name}' configured successfully.")
            except Exception as e:
                logger.error(f"Error configuring plugin {plugin_name}: {e}", exc_info=True)
                QMessageBox.warning(self, "Plugin Error", f"Error configuring plugin: {str(e)}")
                
    def on_new_project(self):
        """Create a new project"""
        try:
            # Ask for project name
            name, ok = QInputDialog.getText(
                self, "New Project", "Enter project name:"
            )
            if not ok or not name:
                return
                
            # Create project
            from app.models.Project import Project
            self.current_project = Project(name, f"Created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Clear existing data
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.clear_markers()
            
            if hasattr(self.ui, 'analysisTextBrowser'):
                self.ui.analysisTextBrowser.clear()
            
            # Update window title
            self.setWindowTitle(f"CreepyAI - {self.current_project.name}")
            
            # Set default file path
            safe_name = "".join([c if c.isalnum() else "_" for c in name])
            default_path = os.path.join(self.project_dir, f"{safe_name}.creepy")
            self.current_project.file_path = default_path
            
            QMessageBox.information(self, "New Project", f"Created new project: {name}")
        except Exception as e:
            logger.error(f"Error creating new project: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to create project: {str(e)}")
        
    def on_open_project(self):
        """Open an existing project"""
        try:
            # Show file dialog to select project file
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Project", self.project_dir, 
                "CreepyAI Projects (*.creepy);;All Files (*)"
            )
            
            if file_path:
                # Load the project
                from app.models.Project import Project
                self.current_project = Project.load(file_path)
                
                if self.current_project:
                    QMessageBox.information(self, "Open Project", f"Opened project: {self.current_project.name}")
                    
                    # Update window title
                    self.setWindowTitle(f"CreepyAI - {self.current_project.name}")
                    
                    # Display project locations
                    if hasattr(self.current_project, 'locations') and self.current_project.locations:
                        self._display_plugin_locations(
                            [loc.to_dict() for loc in self.current_project.locations],
                            f"Project: {self.current_project.name}"
                        )
                else:
                    QMessageBox.warning(self, "Open Project", "Failed to load the project.")
        except Exception as e:
            logger.error(f"Error opening project: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to open project: {str(e)}")
        
    def on_save_project(self):
        """Save the current project"""
        if not self.current_project:
            QMessageBox.warning(self, "Save Project", "No active project to save.")
            return
            
        try:
            # Update locations in project
            self.current_project.locations = self.current_locations
            
            # Check if project has a file path
            if not hasattr(self.current_project, 'file_path') or not self.current_project.file_path:
                # Ask for file path
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Project", self.project_dir, 
                    "CreepyAI Projects (*.creepy);;All Files (*)"
                )
                if not file_path:
                    return
                
                # Add extension if missing
                if not file_path.endswith('.creepy'):
                    file_path += '.creepy'
                
                self.current_project.file_path = file_path
            
            # Save the project
            self.current_project.save()
            
            QMessageBox.information(self, "Save Project", f"Project saved successfully.")
        except Exception as e:
            logger.error(f"Error saving project: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to save project: {str(e)}")
        
    def on_import_locations(self):
        """Import locations from a file"""
        try:
            # Show file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Locations", "", 
                "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
            )
            if not file_path:
                return
                
            # Determine file type
            if file_path.endswith('.json'):
                # Import from JSON
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Handle different JSON formats
                locations = []
                
                if isinstance(data, list):
                    # Direct list of locations
                    locations = data
                elif isinstance(data, dict) and 'locations' in data:
                    # Locations in a 'locations' key
                    locations = data['locations']
                elif isinstance(data, dict) and 'features' in data:
                    # GeoJSON format
                    for feature in data['features']:
                        if feature.get('geometry', {}).get('type') == 'Point':
                            coords = feature['geometry']['coordinates']
                            properties = feature.get('properties', {})
                            
                            location = {
                                'lon': coords[0],
                                'lat': coords[1],
                                'name': properties.get('name', 'Imported Location'),
                                'source': 'Imported GeoJSON'
                            }
                            
                            # Add all other properties
                            for key, value in properties.items():
                                if key != 'name':
                                    location[key] = value
                                    
                            locations.append(location)
                
                # Display imported locations
                if locations:
                    self._display_plugin_locations(locations, f"Imported: {os.path.basename(file_path)}")
                else:
                    QMessageBox.warning(self, "Import Locations", "No valid locations found in file.")
                    
            elif file_path.endswith('.csv'):
                # Show not implemented
                QMessageBox.information(self, "Import Locations", "CSV import not implemented yet.")
            else:
                QMessageBox.warning(self, "Import Locations", "Unsupported file format.")
        except Exception as e:
            logger.error(f"Error importing locations: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to import locations: {str(e)}")
        
    def on_export_locations(self):
        """Export locations to a file"""
        if not self.current_locations:
            QMessageBox.warning(self, "Export Locations", "No locations to export.")
            return
            
        try:
            # Show file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Locations", "", 
                "JSON Files (*.json);;GeoJSON Files (*.geojson);;CSV Files (*.csv);;All Files (*)"
            )
            if not file_path:
                return
                
            # Determine export format
            if file_path.endswith('.json'):
                # Export as JSON
                with open(file_path, 'w') as f:
                    json.dump(self.current_locations, f, indent=2)
                    
            elif file_path.endswith('.geojson'):
                # Export as GeoJSON
                geojson = {
                    "type": "FeatureCollection",
                    "features": []
                }
                
                for location in self.current_locations:
                    # Skip if missing coordinates
                    lat = lon = None
                    if 'lat' in location and 'lon' in location:
                        lat = location['lat']
                        lon = location['lon']
                    elif 'latitude' in location and 'longitude' in location:
                        lat = location['latitude']
                        lon = location['longitude']
                        
                    if lat is None or lon is None:
                        continue
                        
                    # Create properties from all fields except lat/lon
                    properties = {}
                    for key, value in location.items():
                        if key not in ['lat', 'lon', 'latitude', 'longitude']:
                            properties[key] = value
                            
                    # Create feature
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "properties": properties
                    }
                    
                    geojson["features"].append(feature)
                
                # Write GeoJSON file
                with open(file_path, 'w') as f:
                    json.dump(geojson, f, indent=2)
                    
            elif file_path.endswith('.csv'):
                # Show not implemented
                QMessageBox.information(self, "Export Locations", "CSV export not implemented yet.")
                return
            else:
                QMessageBox.warning(self, "Export Locations", "Unsupported file format.")
                return
                
            QMessageBox.information(self, "Export Locations", f"Exported {len(self.current_locations)} locations to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting locations: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to export locations: {str(e)}")
        
    def on_manage_plugins(self):
        """Open plugin management dialog"""
        QMessageBox.information(self, "Manage Plugins", 
                               "Plugin management is available in the Plugins tab.")
        
        # Switch to plugins tab if available
        for i in range(self.ui.rightTabWidget.count()):
            if self.ui.rightTabWidget.tabText(i).lower() == "plugins":
                self.ui.rightTabWidget.setCurrentIndex(i)
                break

    def on_settings(self):
        """Open settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet.")

    def load_settings(self):
        """Load application settings"""
        settings_file = os.path.join(os.path.expanduser("~"), ".creepyai", "settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            except Exception as e:
                logger.error(f"Error loading settings: {e}", exc_info=True)
                self.settings = {}
        else:
            self.settings = {}

    def save_settings(self):
        """Save application settings"""
        settings_file = os.path.join(os.path.expanduser("~"), ".creepyai", "settings.json")
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)

    def apply_icons(self):
        """Apply icons to UI elements"""
        try:
            from app.gui.resources.icons import Icons
            Icons.setup_action_icons(self)
        except ImportError:
            logger.warning("Could not import Icons module")
        except Exception as e:
            logger.error(f"Error applying icons: {e}", exc_info=True)

    def _display_plugin_locations(self, locations, title="Plugin Results"):
        """Display location results from a plugin on the map and in the analysis view"""
        if not locations:
            QMessageBox.information(self, title, "No location data found.")
            return

        # Standardize locations first
        try:
            from app.core.plugins.standardize import LocationStandardizer
            locations = LocationStandardizer.standardize_locations(locations)
        except ImportError:
            # Continue with original locations if standardizer not available
            pass
        
        # Store the locations
        self.current_locations = locations
        
        # Clear previous results
        if hasattr(self, 'map_view') and self.map_view:
            self.map_view.clear_markers()
        
        # Clear analysis text
        if hasattr(self.ui, 'analysisTextBrowser'):
            self.ui.analysisTextBrowser.clear()
            self.ui.analysisTextBrowser.append(f"<h2>{title}</h2>")
        
        # Add each location to the map and analysis view
        for i, location in enumerate(locations):
            # Skip if missing lat/lon
            if 'lat' not in location or 'lon' not in location:
                continue
                
            lat = float(location['lat'])
            lon = float(location['lon'])
            name = location.get('name', f"Location {i+1}")
            
            # Build info string for popup
            info_parts = []
            exclude_keys = ['lat', 'lon', 'latitude', 'longitude', 'name', 'title']
            
            for key, value in location.items():
                if key not in exclude_keys and not key.startswith('_'):
                    # Skip complex nested objects
                    if isinstance(value, dict) or isinstance(value, list):
                        continue
                    info_parts.append(f"{key}: {value}")
            
            info = "<br>".join(info_parts)
            
            # Add to map
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.add_marker(lat, lon, name, info)
            
            # Add to analysis view
            if hasattr(self.ui, 'analysisTextBrowser'):
                self.ui.analysisTextBrowser.append(f"<p><b>{name}</b><br>")
                self.ui.analysisTextBrowser.append(f"Coordinates: {lat}, {lon}<br>")
                for part in info_parts[:5]:  # Limit to first 5 properties
                    self.ui.analysisTextBrowser.append(f"{part}<br>")
                if len(info_parts) > 5:
                    self.ui.analysisTextBrowser.append("(more properties available)...")
                self.ui.analysisTextBrowser.append("</p>")
        
        # Center map on first result
        if locations and hasattr(self, 'map_view') and self.map_view:
            first_loc = locations[0]
            lat = float(first_loc['lat'])
            lon = float(first_loc['lon'])
            self.map_view.center_map(lat, lon, 12)
        
        # Switch to appropriate tab
        if hasattr(self.ui, 'rightTabWidget'):
            # Find the analysis tab - it might be named differently
            for i in range(self.ui.rightTabWidget.count()):
                tab_name = self.ui.rightTabWidget.tabText(i).lower()
                if 'analysis' in tab_name or 'result' in tab_name:
                    self.ui.rightTabWidget.setCurrentIndex(i)
                    break

    def on_configure_plugin_clicked(self):
        """Configure the selected plugin"""
        selected_items = self.ui.pluginListWidget.selectedItems()
        if not selected_items:
            return
            
        plugin_name = selected_items[0].data(Qt.UserRole)
        if not plugin_name:
            return  # It's a category header, not a plugin
            
        logger.info(f"Configuring plugin: {plugin_name}")
        
        plugin = self.plugin_manager.get_plugin(plugin_name)
        
        try:
            if plugin and hasattr(plugin, 'configure'):
                # Check if plugin has a configuration UI
                if hasattr(plugin, 'get_configuration_options'):
                    # Plugin has configuration options, show a configuration dialog
                    from app.gui.plugin_config_dialog import PluginConfigDialog
                    dialog = PluginConfigDialog(self, plugin)
                    if dialog.exec_():
                        QMessageBox.information(self, "Plugin Configuration", 
                                            f"Plugin '{plugin_name}' configured successfully.")
                else:
                    # Simple configure method
                    result = plugin.configure()
                    QMessageBox.information(self, "Plugin Configuration", 
                                          f"Plugin '{plugin_name}' configured successfully.")
            else:
                QMessageBox.warning(self, "Plugin Configuration",
                                  f"Plugin '{plugin_name}' does not support configuration.")
        except Exception as e:
            logger.error(f"Error configuring plugin {plugin_name}: {e}", exc_info=True)
            QMessageBox.warning(self, "Plugin Error", f"Error configuring plugin: {str(e)}")

    # Placeholder methods for other UI actions
    def on_new_project(self):
        """Create a new project"""
        try:
            # Initialize a new project with default settings
            from app.models.Project import Project
            self.current_project = Project("New Project", "Created on " + datetime.datetime.now().strftime("%Y-%m-%d"))
            QMessageBox.information(self, "New Project", "Created a new project.")
            
            # Clear the map
            if hasattr(self, 'map_view') and self.map_view:
                self.map_view.clear_markers()
                
            # Clear the analysis view
            self.ui.analysisTextBrowser.clear()
            
            # Update window title
            self.setWindowTitle(f"CreepyAI - {self.current_project.name}")
            
        except Exception as e:
            logger.error(f"Error creating new project: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to create new project: {str(e)}")
        
    def on_open_project(self):
        """Open an existing project"""
        try:
            # Show file dialog to select project file
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Project", "", 
                "CreepyAI Projects (*.creepy);;All Files (*)"
            )
            
            if file_path:
                # Load the project
                from app.models.Project import Project
                self.current_project = Project.load(file_path)
                
                if self.current_project:
                    QMessageBox.information(self, "Open Project", f"Opened project: {self.current_project.name}")
                    
                    # Update window title
                    self.setWindowTitle(f"CreepyAI - {self.current_project.name}")
                    
                    # Display project locations
                    if hasattr(self.current_project, 'locations') and self.current_project.locations:
                        self._display_plugin_locations(
                            [loc.to_dict() for loc in self.current_project.locations],
                            f"Project: {self.current_project.name}"
                        )
                else:
                    QMessageBox.warning(self, "Open Project", "Failed to load the project.")
        except Exception as e:
            logger.error(f"Error opening project: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to open project: {str(e)}")
        
    def on_save_project(self):
        """Save the current project"""
        try:
            if not hasattr(self, 'current_project') or not self.current_project:
                # No project to save
                QMessageBox.warning(self, "Save Project", "No active project to save.")
                return
                
            if hasattr(self.current_project, 'file_path') and self.current_project.file_path:
                # Project has a path, save directly
                self.current_project.save()
                QMessageBox.information(self, "Save Project", "Project saved successfully.")
            else:
                # No path yet, ask for one
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Project", "", 
                    "CreepyAI Projects (*.creepy);;All Files (*)"
                )
                
                if file_path:
                    if not file_path.endswith('.creepy'):
                        file_path += '.creepy'
                    self.current_project.save(file_path)
                    QMessageBox.information(self, "Save Project", "Project saved successfully.")
        except Exception as e:
            logger.error(f"Error saving project: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Failed to save project: {str(e)}")
        
    def on_import_locations(self):
        QMessageBox.information(self, "Import Locations", "Import locations functionality not implemented yet.")
        
    def on_export_locations(self):
        QMessageBox.information(self, "Export Locations", "Export locations functionality not implemented yet.")
        
    def on_manage_plugins(self):
        QMessageBox.information(self, "Manage Plugins", "Plugin management functionality not implemented yet.")
        
    def on_settings(self):
        QMessageBox.information(self, "Settings", "Settings functionality not implemented yet.")
        
    def on_about(self):
        QMessageBox.about(self, "About CreepyAI", 
                         """<h2>CreepyAI</h2>
                         <p>Version 1.0</p>
                         <p>Geolocation OSINT AI Tool</p>
                         <p>A powerful tool for geolocation intelligence analysis.</p>""")
        
    def on_documentation(self):
        QMessageBox.information(self, "Documentation", "Documentation not available yet.")
        
    def on_add_location(self):
        QMessageBox.information(self, "Add Location", "Add location functionality not implemented yet.")
        
    def on_zoom_in(self):
        # Zoom in on the map
        if hasattr(self, 'map_view') and self.map_view:
            # Get current center and zoom, then increase zoom by 1
            # This is placeholder - would need to implement getting current center and zoom from the map
            self.map_view.center_map(37.7749, -122.4194, 14)
        
    def on_zoom_out(self):
        # Zoom out on the map
        if hasattr(self, 'map_view') and self.map_view:
            # Get current center and zoom, then decrease zoom by 1
            # This is placeholder - would need to implement getting current center and zoom from the map
            self.map_view.center_map(37.7749, -122.4194, 10)

    def on_configure_plugin_clicked(self):
        """Configure the selected plugin"""
        selected_items = self.ui.pluginListWidget.selectedItems()
        if not selected_items:
            return
            
        plugin_name = selected_items[0].data(Qt.UserRole)
        if not plugin_name:
            return  # It's a category header, not a plugin
            
        logger.info(f"Configuring plugin: {plugin_name}")
        
        plugin = self.plugin_manager.get_plugin(plugin_name)
        
        try:
            if plugin and hasattr(plugin, 'configure'):
                # Check if plugin has a configuration UI
                if hasattr(plugin, 'get_configuration_options'):
                    # Plugin has configuration options, show a configuration dialog
                    from app.gui.plugin_config_dialog import PluginConfigDialog
                    dialog = PluginConfigDialog(self, plugin)
                    if dialog.exec_():
                        QMessageBox.information(self, "Plugin Configuration", 
                                            f"Plugin '{plugin_name}' configured successfully.")
                else:
                    # Simple configure method
                    result = plugin.configure()
                    QMessageBox.information(self, "Plugin Configuration", 
                                          f"Plugin '{plugin_name}' configured successfully.")
            else:
                QMessageBox.warning(self, "Plugin Configuration",
                                  f"Plugin '{plugin_name}' does not support configuration.")
        except Exception as e:
            logger.error(f"Error configuring plugin {plugin_name}: {e}", exc_info=True)
            QMessageBox.warning(self, "Plugin Error", f"Error configuring plugin: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("Starting CreepyAI application...")
        app = QApplication(sys.argv)
        main_window = CreepyAIMain()
        main_window.show()
        logger.info("CreepyAI application started successfully.")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
