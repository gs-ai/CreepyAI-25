"""
Fallback UI for CreepyAI
Used when WebEngine is not available (no map support)
"""

import os
import logging
from typing import Optional, List, Dict, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTabWidget, QListWidget, QListWidgetItem,
    QTextEdit, QToolBar, QAction, QStatusBar, QFileDialog,
    QMessageBox, QApplication, QSplitter, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from app.plugins.plugin_manager import PluginManager
from app.core.include.button_styles import ButtonStyles

logger = logging.getLogger(__name__)

class FallbackMainWindow(QMainWindow):
    """
    Fallback main window for when WebEngine is not available
    Provides basic functionality without map support
    """
    
    def __init__(self, plugin_manager: Optional[PluginManager] = None):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.setup_ui()
        
        self.setWindowTitle("CreepyAI - Limited Functionality Mode")
        self.resize(1000, 700)
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_label = QLabel("Limited functionality mode - WebEngine not available")
        self.statusBar.addWidget(self.status_label)
        
        # Add warning message about missing WebEngine
        warning_label = QLabel(
            "<html><body style='background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px;'>"
            "<h2>⚠️ Limited Functionality Mode</h2>"
            "<p>CreepyAI is running in limited functionality mode because WebEngine is not available.</p>"
            "<p>Map visualization features are disabled. Please install PyQt5-WebEngine to enable full functionality.</p>"
            "<p>You can still use data export and basic plugin functionality.</p>"
            "</body></html>"
        )
        warning_label.setWordWrap(True)
        main_layout.addWidget(warning_label)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)  # Give it stretch factor
        
        # Left panel (plugin/data selection)
        left_panel = QTabWidget()
        splitter.addWidget(left_panel)
        
        # Add plugin tab
        plugin_widget = self.create_plugin_tab()
        left_panel.addTab(plugin_widget, "Plugins")
        
        # Add data tab
        data_widget = self.create_data_tab()
        left_panel.addTab(data_widget, "Data")
        
        # Right panel (details and reports)
        right_panel = QTabWidget()
        splitter.addWidget(right_panel)
        
        # Add details tab
        details_widget = self.create_details_tab()
        right_panel.addTab(details_widget, "Details")
        
        # Add export tab
        export_widget = self.create_export_tab()
        right_panel.addTab(export_widget, "Export")
        
        # Set initial splitter sizes
        splitter.setSizes([300, 700])
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Get icons path
        self.icon_path = os.path.join("app", "resources", "icons")
        
        # Add basic actions
        # New project
        new_action = QAction(self.get_icon("new-project-icon.png"), "New Project", self)
        new_action.setStatusTip("Create new project")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # Open project
        open_action = QAction(self.get_icon("open-icon.png"), "Open Project", self)
        open_action.setStatusTip("Open existing project")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # Save project
        save_action = QAction(self.get_icon("save-icon.png"), "Save", self)
        save_action.setStatusTip("Save current project")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction(self.get_icon("export-icon.png"), "Export Data", self)
        export_action.setStatusTip("Export data to file")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        # Import action
        import_action = QAction(self.get_icon("import-icon.png"), "Import Data", self)
        import_action.setStatusTip("Import data from file")
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_data)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # Help action
        help_action = QAction(self.get_icon("help-icon.png"), "Help", self)
        help_action.setStatusTip("Show help")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)
        
        # About action
        about_action = QAction(self.get_icon("about-icon.png"), "About", self)
        about_action.setStatusTip("About CreepyAI")
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def get_icon(self, icon_name):
        """Get an icon with fallback to system icons if file not found"""
        icon_path = os.path.join(self.icon_path, icon_name)
        
        # Check if icon file exists
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        
        # Use system theme icon as fallback
        system_icon_name = icon_name.replace("-icon.png", "").replace("-", "_")
        system_icon = QIcon.fromTheme(system_icon_name)
        
        # If system icon doesn't exist, use a standard icon as fallback
        if system_icon.isNull():
            # Map of standard fallback icons
            fallbacks = {
                "new-project-icon.png": QStyle.SP_FileIcon,
                "open-icon.png": QStyle.SP_DirOpenIcon,
                "save-icon.png": QStyle.SP_DialogSaveButton,
                "export-icon.png": QStyle.SP_DialogSaveButton,
                "import-icon.png": QStyle.SP_DialogOpenButton,
                "help-icon.png": QStyle.SP_DialogHelpButton,
                "about-icon.png": QStyle.SP_MessageBoxInformation
            }
            
            # Get style from application
            style = QApplication.style()
            
            # Use appropriate standard icon or default
            if icon_name in fallbacks:
                return style.standardIcon(fallbacks[icon_name])
            else:
                return style.standardIcon(QStyle.SP_TitleBarMenuButton)
        
        return system_icon
    
    def create_plugin_tab(self) -> QWidget:
        """Create the plugins tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a list of available plugins
        plugin_group = QGroupBox("Available Plugins")
        plugin_layout = QVBoxLayout(plugin_group)
        
        self.plugin_list = QListWidget()
        plugin_layout.addWidget(self.plugin_list)
        
        # Add plugin actions
        actions_layout = QHBoxLayout()
        
        # Configure plugin button
        configure_btn = QPushButton("Configure Plugin")
        configure_btn.setIcon(self.get_icon("configure-icon.png"))
        ButtonStyles.primary_button(configure_btn)
        configure_btn.clicked.connect(self.configure_plugin)
        actions_layout.addWidget(configure_btn)
        
        # Run plugin button
        run_btn = QPushButton("Run Plugin")
        run_btn.setIcon(self.get_icon("run-icon.png"))
        ButtonStyles.secondary_button(run_btn)
        run_btn.clicked.connect(self.run_plugin)
        actions_layout.addWidget(run_btn)
        
        plugin_layout.addLayout(actions_layout)
        layout.addWidget(plugin_group)
        
        # Plugin details section
        details_group = QGroupBox("Plugin Details")
        details_layout = QVBoxLayout(details_group)
        
        self.plugin_details = QTextEdit()
        self.plugin_details.setReadOnly(True)
        details_layout.addWidget(self.plugin_details)
        
        layout.addWidget(details_group)
        
        # Populate plugin list if we have the plugin manager
        if self.plugin_manager:
            self.populate_plugin_list()
        else:
            # For now, just add dummy plugins
            self.plugin_list.addItem("Facebook")
            self.plugin_list.addItem("Instagram")
            self.plugin_list.addItem("Twitter")
            self.plugin_list.addItem("LinkedIn")
            self.plugin_list.addItem("Pinterest")
            self.plugin_list.addItem("Snapchat")
            self.plugin_list.addItem("TikTok")
            self.plugin_list.addItem("Yelp")
        
        # Connect signals
        self.plugin_list.currentItemChanged.connect(self.show_plugin_details)
        
        return tab
    
    def create_data_tab(self) -> QWidget:
        """Create the data tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data sources section
        sources_group = QGroupBox("Data Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        self.data_list = QListWidget()
        sources_layout.addWidget(self.data_list)
        
        # Add data source actions
        actions_layout = QHBoxLayout()
        
        # Add source button
        add_btn = QPushButton("Add Source")
        add_btn.setIcon(self.get_icon("add-icon.png"))
        ButtonStyles.primary_button(add_btn)
        add_btn.clicked.connect(self.add_data_source)
        actions_layout.addWidget(add_btn)
        
        # Remove source button
        remove_btn = QPushButton("Remove Source")
        remove_btn.setIcon(self.get_icon("remove-icon.png"))
        ButtonStyles.danger_button(remove_btn)
        remove_btn.clicked.connect(self.remove_data_source)
        actions_layout.addWidget(remove_btn)
        
        sources_layout.addLayout(actions_layout)
        layout.addWidget(sources_group)
        
        # Filter section
        filter_group = QGroupBox("Data Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        # Date range filter
        date_label = QLabel("Date Range:")
        filter_layout.addWidget(date_label)
        
        date_layout = QHBoxLayout()
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate().addYears(-1))
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate())
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(end_date)
        filter_layout.addLayout(date_layout)
        
        # Apply button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.setIcon(self.get_icon("filter-icon.png"))
        ButtonStyles.primary_button(apply_btn)
        filter_layout.addWidget(apply_btn)
        
        layout.addWidget(filter_group)
        
        return tab
    
    def create_details_tab(self) -> QWidget:
        """Create the details tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create a text view for details
        details_label = QLabel("Location Details")
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select a location to view details")
        layout.addWidget(self.details_text)
        
        # Summary statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        # Add sample statistics
        stats_layout.addWidget(QLabel("Total Locations: 0"))
        stats_layout.addWidget(QLabel("Date Range: N/A"))
        stats_layout.addWidget(QLabel("Sources: 0"))
        
        layout.addWidget(stats_group)
        
        return tab
    
    def create_export_tab(self) -> QWidget:
        """Create the export tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "JSON", "KML", "HTML Report"])
        format_layout.addWidget(self.format_combo)
        
        options_layout.addLayout(format_layout)
        
        # Include options
        self.include_metadata = QCheckBox("Include metadata")
        self.include_metadata.setChecked(True)
        options_layout.addWidget(self.include_metadata)
        
        self.include_context = QCheckBox("Include context data")
        self.include_context.setChecked(True)
        options_layout.addWidget(self.include_context)
        
        layout.addWidget(options_group)
        
        # Export actions
        actions_layout = QHBoxLayout()
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.setIcon(self.get_icon("export-icon.png"))
        ButtonStyles.primary_button(export_btn)
        export_btn.clicked.connect(self.export_data)
        actions_layout.addWidget(export_btn)
        
        # Preview button
        preview_btn = QPushButton("Preview")
        preview_btn.setIcon(self.get_icon("preview-icon.png"))
        ButtonStyles.secondary_button(preview_btn)
        preview_btn.clicked.connect(self.preview_export)
        actions_layout.addWidget(preview_btn)
        
        layout.addLayout(actions_layout)
        
        # Preview area
        preview_group = QGroupBox("Export Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Click Preview to see data")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        return tab
    
    def populate_plugin_list(self):
        """Populate the list of plugins"""
        self.plugin_list.clear()
        
        try:
            from app.plugin_registry import instantiate_plugins
            plugins = instantiate_plugins()
            
            for plugin in plugins:
                self.plugin_list.addItem(plugin.name)
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}")
            self.statusBar.showMessage(f"Error loading plugins: {e}", 5000)
    
    def show_plugin_details(self, current, previous):
        """Show details for the selected plugin"""
        if not current:
            return
        
        plugin_name = current.text()
        
        try:
            # Try to get the actual plugin object
            from app.plugin_registry import get_plugin_by_name
            plugin = get_plugin_by_name(plugin_name)
            
            if plugin:
                details = f"<h3>{plugin.name}</h3>"
                details += f"<p>{plugin.description}</p>"
                details += f"<p><b>Version:</b> {getattr(plugin, 'version', '1.0.0')}</p>"
                
                if hasattr(plugin, 'author'):
                    details += f"<p><b>Author:</b> {plugin.author}</p>"
                    
                self.plugin_details.setHtml(details)
            else:
                self.plugin_details.setHtml(f"<h3>{plugin_name}</h3><p>Plugin information not available</p>")
                
        except Exception as e:
            logger.error(f"Failed to load plugin details: {e}")
            self.plugin_details.setHtml(f"<h3>{plugin_name}</h3><p>Error loading plugin details: {str(e)}</p>")
    
    def configure_plugin(self):
        """Configure the selected plugin"""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Configure Plugin", "Please select a plugin to configure")
            return
        
        plugin_name = current_item.text()
        QMessageBox.information(self, "Configure Plugin", f"Would configure plugin: {plugin_name}")
    
    def run_plugin(self):
        """Run the selected plugin"""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "Run Plugin", "Please select a plugin to run")
            return
        
        plugin_name = current_item.text()
        QMessageBox.information(self, "Run Plugin", f"Would run plugin: {plugin_name}")
    
    def add_data_source(self):
        """Add a new data source"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data Source", "", "All Files (*);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            self.data_list.addItem(os.path.basename(file_path))
            self.statusBar.showMessage(f"Added data source: {file_path}", 5000)
    
    def remove_data_source(self):
        """Remove the selected data source"""
        current_item = self.data_list.currentItem()
        if not current_item:
            return
            
        row = self.data_list.row(current_item)
        self.data_list.takeItem(row)
    
    def new_project(self):
        """Create a new project"""
        QMessageBox.information(self, "New Project", "Would create a new project")
    
    def open_project(self):
        """Open an existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "CreepyAI Projects (*.cai);;All Files (*)"
        )
        
        if file_path:
            self.statusBar.showMessage(f"Opened project: {file_path}", 5000)
    
    def save_project(self):
        """Save the current project"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "CreepyAI Projects (*.cai);;All Files (*)"
        )
        
        if file_path:
            self.statusBar.showMessage(f"Saved project: {file_path}", 5000)
    
    def export_data(self):
        """Export data to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv);;JSON Files (*.json);;KML Files (*.kml);;HTML Files (*.html);;All Files (*)"
        )
        
        if file_path:
            self.statusBar.showMessage(f"Exported data to: {file_path}", 5000)
    
    def import_data(self):
        """Import data from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Data", "", "All Files (*);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            self.statusBar.showMessage(f"Imported data from: {file_path}", 5000)
    
    def preview_export(self):
        """Preview the export data"""
        format = self.format_combo.currentText()
        
        # Create a sample preview
        if format == "JSON":
            preview = """[
  {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timestamp": "2023-01-15T12:30:45",
    "source": "Sample Source",
    "context": "Sample context data for this location"
  },
  {
    "latitude": 34.0522,
    "longitude": -118.2437,
    "timestamp": "2023-01-16T08:15:30",
    "source": "Sample Source",
    "context": "Another sample location context"
  }
]"""
        elif format == "CSV":
            preview = """latitude,longitude,timestamp,source,context
40.7128,-74.0060,2023-01-15T12:30:45,Sample Source,Sample context data for this location
34.0522,-118.2437,2023-01-16T08:15:30,Sample Source,Another sample location context"""
        elif format == "KML":
            preview = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>CreepyAI Export</name>
    <Placemark>
      <name>Sample Location 1</name>
      <description>Sample context data for this location</description>
      <Point>
        <coordinates>-74.0060,40.7128,0</coordinates>
      </Point>
    </Placemark>
    <Placemark>
      <name>Sample Location 2</name>
      <description>Another sample location context</description>
      <Point>
        <coordinates>-118.2437,34.0522,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>"""
        else:  # HTML Report
            preview = """<!DOCTYPE html>
<html>
<head>
    <title>CreepyAI Export</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>CreepyAI Export</h1>
    <table>
        <tr>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Timestamp</th>
            <th>Source</th>
            <th>Context</th>
        </tr>
        <tr>
            <td>40.7128</td>
            <td>-74.0060</td>
            <td>2023-01-15T12:30:45</td>
            <td>Sample Source</td>
            <td>Sample context data for this location</td>
        </tr>
        <tr>
            <td>34.0522</td>
            <td>-118.2437</td>
            <td>2023-01-16T08:15:30</td>
            <td>Sample Source</td>
            <td>Another sample location context</td>
        </tr>
    </table>
</body>
</html>"""
        
        self.preview_text.setPlainText(preview)
    
    def show_help(self):
        """Show help information"""
        help_text = """<h3>CreepyAI Help</h3>
<p>CreepyAI is a tool for extracting, analyzing, and visualizing location data.</p>

<h4>Limited Functionality Mode</h4>
<p>You are currently running in limited functionality mode because PyQt5-WebEngine is not available. This means that map visualization is not possible.</p>

<h4>Available Features:</h4>
<ul>
    <li>Configure and run plugins to extract location data</li>
    <li>View location details</li>
    <li>Export data to various formats</li>
</ul>

<h4>To enable full functionality:</h4>
<pre>pip install PyQt5-WebEngine</pre>

<h4>For more information, visit:</h4>
<p><a href="https://creepyai.example.com/docs">https://creepyai.example.com/docs</a></p>"""
        
        from PyQt5.QtWidgets import QTextBrowser
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("CreepyAI Help")
        help_dialog.resize(600, 400)
        
        layout = QVBoxLayout(help_dialog)
        
        text_browser = QTextBrowser()
        text_browser.setHtml(help_text)
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        ButtonStyles.secondary_button(close_button)
        close_button.clicked.connect(help_dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        help_dialog.exec_()
    
    def show_about(self):
        """Show about dialog"""
        try:
            from app.gui.ui.dialogs.about_dialog import AboutDialog
            about_dialog = AboutDialog(self)
            about_dialog.exec_()
        except ImportError as e:
            QMessageBox.information(self, "About CreepyAI", 
                                  "CreepyAI - OSINT Location Intelligence Tool\n\nVersion 1.0.0")
            logger.error(f"Could not load about dialog: {e}")
