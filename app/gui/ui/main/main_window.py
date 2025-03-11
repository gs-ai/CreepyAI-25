"""
Main Window for CreepyAI
Integrates all components into the main application interface
"""

import sys
import logging
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QStatusBar
from PyQt5.QtCore import Qt

from app.gui.ui.main.toolbar_manager import ToolbarManager
from app.controllers.map_controller import MapController
from app.models.location_data import LocationDataModel
from app.gui.ui.components.data_visualization import DataVisualization
from app.gui.ui.components.data_analysis import DataAnalysis

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window for CreepyAI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CreepyAI")
        self.resize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Initialize components
        self.toolbar_manager = ToolbarManager(self)
        self.map_view = QWebEngineView()
        self.map_controller = MapController(self.map_view)
        self.data_visualization = DataVisualization()
        self.data_analysis = DataAnalysis()
        
        # Set up layout
        layout.addWidget(self.map_view, 3)
        layout.addWidget(self.data_visualization, 1)
        layout.addWidget(self.data_analysis, 1)
        
        # Set up toolbars
        self.setup_toolbars()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.map_controller.mapLoaded.connect(self.on_map_loaded)
        self.map_controller.mapError.connect(self.on_map_error)
        self.map_controller.locationSelected.connect(self.on_location_selected)
        
        # Initialize location model
        self.location_model = LocationDataModel()
        self.map_controller.set_location_model(self.location_model)
        self.data_visualization.set_location_model(self.location_model)
        self.data_analysis.set_location_model(self.location_model)
        
        logger.info("Main window initialized")
    
    def setup_toolbars(self):
        """Set up the application toolbars"""
        main_toolbar = self.toolbar_manager.create_main_toolbar()
        map_toolbar = self.toolbar_manager.create_map_toolbar()
        plugin_toolbar = self.toolbar_manager.create_plugin_toolbar()
        
        # Add actions to toolbars
        self.toolbar_manager.add_action(
            "main", "new_project", "New Project", self.new_project,
            icon_name="new-project-icon.png", status_tip="Create a new project", shortcut="Ctrl+N"
        )
        self.toolbar_manager.add_action(
            "main", "open_project", "Open Project", self.open_project,
            icon_name="open-icon.png", status_tip="Open an existing project", shortcut="Ctrl+O"
        )
        self.toolbar_manager.add_action(
            "main", "save_project", "Save Project", self.save_project,
            icon_name="save-icon.png", status_tip="Save the current project", shortcut="Ctrl+S"
        )
        self.toolbar_manager.add_separator("main")
        self.toolbar_manager.add_action(
            "main", "import_data", "Import Data", self.import_data,
            icon_name="import-icon.png", status_tip="Import data from various sources"
        )
        self.toolbar_manager.add_action(
            "main", "export_data", "Export Data", self.export_data,
            icon_name="export-icon.png", status_tip="Export data to various formats"
        )
        self.toolbar_manager.add_separator("main")
        self.toolbar_manager.add_action(
            "main", "preferences", "Preferences", self.open_preferences,
            icon_name="settings-icon.png", status_tip="Open application preferences"
        )
        
        self.toolbar_manager.add_action(
            "map", "fit_bounds", "Fit Bounds", self.fit_map_bounds,
            icon_name="fit-bounds-icon.png", status_tip="Fit map to show all markers"
        )
        self.toolbar_manager.add_action(
            "map", "toggle_heatmap", "Toggle Heatmap", self.toggle_heatmap,
            icon_name="heatmap-icon.png", status_tip="Toggle heatmap display", checkable=True
        )
        self.toolbar_manager.add_action(
            "map", "toggle_clustering", "Toggle Clustering", self.toggle_clustering,
            icon_name="clustering-icon.png", status_tip="Toggle marker clustering", checkable=True
        )
        
        self.toolbar_manager.add_action(
            "plugin", "manage_plugins", "Manage Plugins", self.manage_plugins,
            icon_name="plugins-icon.png", status_tip="Manage plugins"
        )
    
    def new_project(self):
        """Create a new project"""
        # Implementation for creating a new project
        pass
    
    def open_project(self):
        """Open an existing project"""
        # Implementation for opening an existing project
        pass
    
    def save_project(self):
        """Save the current project"""
        # Implementation for saving the current project
        pass
    
    def import_data(self):
        """Import data from various sources"""
        # Implementation for importing data
        pass
    
    def export_data(self):
        """Export data to various formats"""
        # Implementation for exporting data
        pass
    
    def open_preferences(self):
        """Open application preferences"""
        # Implementation for opening preferences dialog
        pass
    
    def fit_map_bounds(self):
        """Fit map to show all markers"""
        self.map_controller.fit_bounds()
    
    def toggle_heatmap(self, checked: bool):
        """Toggle heatmap display"""
        self.map_controller.toggle_heatmap(checked)
    
    def toggle_clustering(self, checked: bool):
        """Toggle marker clustering"""
        self.map_controller.toggle_clustering(checked)
    
    def manage_plugins(self):
        """Manage plugins"""
        # Implementation for managing plugins
        pass
    
    def on_map_loaded(self, success: bool):
        """Handle map loaded event"""
        if success:
            self.status_bar.showMessage("Map loaded successfully", 5000)
        else:
            self.status_bar.showMessage("Failed to load map", 5000)
    
    def on_map_error(self, error_message: str):
        """Handle map error event"""
        self.status_bar.showMessage(f"Map error: {error_message}", 5000)
    
    def on_location_selected(self, location_id: str):
        """Handle location selected event"""
        location = self.location_model.get_location(location_id)
        if location:
            self.status_bar.showMessage(f"Selected location: {location.context}", 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
