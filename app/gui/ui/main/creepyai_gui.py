"""
Main GUI class for CreepyAI
Integrates all UI components including plugin selector and map display
"""

import os
import logging
import datetime
from typing import Optional, Dict, Any, List

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QAction, QToolBar, QStatusBar, 
    QApplication, QFileDialog, QMessageBox, QLabel,
    QTabWidget, QPushButton, QLineEdit, QDateEdit, QFrame, QComboBox, QToolButton, QMenu
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot, QDate, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

from app.ui.plugin_selector import PluginSelector
from app.controllers.map_controller import MapController
from app.plugins.plugin_manager import PluginManager
from app.plugins.base_plugin import LocationPoint
from app.plugin_registry import instantiate_plugins

logger = logging.getLogger(__name__)

class CreepyAIGUI(QMainWindow):
    """
    Main window for CreepyAI application
    Integrates map view, plugin selector, and search functionality
    """
    
    def __init__(self, plugin_manager: Optional[PluginManager] = None):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.map_controller = None
        self.plugin_selector = None
        self.search_results = []
        
        self.setup_ui()
        self.setup_signals()
        
        self.setWindowTitle("CreepyAI - OSINT Location Intelligence")
        self.resize(1200, 800)
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create and initialize the toolbar
        self.toolbar = self.create_toolbar()
        # No need to add the toolbar to the layout as it's added to the main window directly
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_label = QLabel("Ready")
        self.statusBar.addWidget(self.status_label)
        
        # Create main splitter for sidebar and map
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create sidebar with tabs
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        sidebar_layout.addWidget(self.tabs)
        
        # Create plugin selector tab
        self.plugin_selector = PluginSelector()
        self.tabs.addTab(self.plugin_selector, "Plugins")
        
        # Create search tab
        search_widget = self.create_search_widget()
        self.tabs.addTab(search_widget, "Search")
        
        # Add filters tab
        filters_widget = self.create_filters_widget()
        self.tabs.addTab(filters_widget, "Filters")
        
        # Create map view
        self.map_widget = QWebEngineView()
        
        # Add widgets to splitter
        self.main_splitter.addWidget(sidebar_widget)
        self.main_splitter.addWidget(self.map_widget)
        
        # Set initial splitter sizes (30% sidebar, 70% map)
        self.main_splitter.setSizes([300, 700])
        
        # Initialize map controller
        self.map_controller = MapController(self.map_widget)
        
        # Connect plugin selector to map controller
        self.plugin_selector.connect_to_map_controller(self.map_controller)
    
    def create_toolbar(self) -> QToolBar:
        """Create the main toolbar with common actions"""
        # Create toolbar and set properties
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(True)  # Allow users to move the toolbar if they want
        toolbar.setFloatable(False)  # Prevent it from being floated as a separate window
        toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)  # Allow docking at top or bottom
        
        # Set toolbar style
        toolbar.setStyleSheet("""
            QToolBar {
                border-bottom: 1px solid #cccccc;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                 stop: 0 #f8f8f8, stop: 1 #eeeeee);
                spacing: 2px;
                padding: 2px;
            }
            QToolBar::separator {
                width: 1px;
                background-color: #cccccc;
                margin: 4px 8px;
            }
        """)
        
        # Get icons path for consistency
        self.icon_path = os.path.join("app", "resources", "icons")
        
        # Project section
        # New project action - enhanced with icon and shortcut
        new_action = self.create_action(
            "New Project", 
            "new-project-icon.png", 
            "Create a new project (Ctrl+N)",
            "Ctrl+N", 
            self.new_project
        )
        toolbar.addAction(new_action)
        
        # Open project action
        open_action = self.create_action(
            "Open Project", 
            "open-icon.png", 
            "Open an existing project (Ctrl+O)",
            "Ctrl+O", 
            self.open_project
        )
        toolbar.addAction(open_action)
        
        # Save action
        save_action = self.create_action(
            "Save", 
            "save-icon.png", 
            "Save current project (Ctrl+S)",
            "Ctrl+S", 
            self.save_project
        )
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Map controls section
        # Map Layer section with improved UX
        map_section_label = QLabel("Map Layer: ")
        map_section_label.setStyleSheet("font-weight: bold; margin-right: 5px; margin-left: 5px;")
        toolbar.addWidget(map_section_label)
        
        # Create an enhanced ComboBox with tooltips and better styling
        self.map_layer_combo = QComboBox()
        self.map_layer_combo.setToolTip("Select map type - also available via the map control panel")
        self.map_layer_combo.setStyleSheet("""
            QComboBox {
                min-width: 150px;
                padding: 3px 10px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f8f8f8;
            }
            QComboBox::drop-down {
                width: 20px;
            }
        """)
        
        # Make sure we initialize the map controller before accessing it
        if not hasattr(self, 'map_controller') or self.map_controller is None:
            self.map_controller = MapController(self.map_widget)
        
        try:
            self.map_layer_combo.addItems(self.map_controller.get_available_layers())
            self.map_layer_combo.setCurrentText(self.map_controller.get_current_layer())
        except Exception as e:
            logger.warning(f"Could not initialize map layers: {e}")
            self.map_layer_combo.addItems(["Street Map", "Satellite", "Terrain", "Dark Mode"])
        
        self.map_layer_combo.currentTextChanged.connect(self.change_map_layer)
        toolbar.addWidget(self.map_layer_combo)
        
        # Map help button - enhanced with proper icon and tooltip
        map_help_btn = QPushButton()
        map_help_btn.setIcon(self.get_icon("help-icon.png"))
        map_help_btn.setToolTip("Show map controls help")
        map_help_btn.setMaximumWidth(30)
        map_help_btn.setMaximumHeight(30)
        map_help_btn.setStyleSheet("""
            QPushButton { 
                border-radius: 15px; 
                padding: 5px;
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        map_help_btn.clicked.connect(self.show_map_help)
        toolbar.addWidget(map_help_btn)
        
        toolbar.addSeparator()
        
        # Data actions section
        # Refresh map action
        refresh_action = self.create_action(
            "Refresh Map", 
            "refresh-icon.png", 
            "Refresh map data (F5)",
            "F5", 
            self.refresh_map
        )
        toolbar.addAction(refresh_action)
        
        # Export action
        export_action = self.create_action(
            "Export Data", 
            "export-icon.png", 
            "Export data to file (Ctrl+E)",
            "Ctrl+E", 
            self.export_data
        )
        toolbar.addAction(export_action)
        
        # Import Data action (new)
        import_action = self.create_action(
            "Import Data", 
            "import-icon.png", 
            "Import location data (Ctrl+I)",
            "Ctrl+I", 
            self.import_data
        )
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # Configure button with dropdown menu
        self.config_button = QToolButton()
        self.config_button.setText("Configure")
        self.config_button.setIcon(self.get_icon("configure-icon.png"))
        self.config_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.config_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.config_button.setToolTip("Configure application settings")
        self.config_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f5f5f5;
                padding: 3px 10px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
            QToolButton::menu-button {
                width: 16px;
                border-left: 1px solid #ccc;
            }
        """)
        
        # Create dropdown menu for configuration options
        config_menu = QMenu()
        
        # Application settings action
        app_settings_action = QAction(self.get_icon("settings-icon.png"), 
                                    "Application Settings", self)
        app_settings_action.triggered.connect(self.show_preferences_dialog)
        app_settings_action.setToolTip("Configure general application settings")
        config_menu.addAction(app_settings_action)
        
        # Plugin configuration action
        plugin_config_action = QAction(self.get_icon("plugins-icon.png"), 
                                     "Plugin Configuration", self)
        plugin_config_action.triggered.connect(self.show_plugin_config_dialog)
        plugin_config_action.setToolTip("Configure data source plugins")
        config_menu.addAction(plugin_config_action)
        
        # Map settings action
        map_settings_action = QAction(self.get_icon("map-icon.png"), 
                                    "Map Settings", self)
        map_settings_action.triggered.connect(self.show_map_settings)
        map_settings_action.setToolTip("Configure map display settings")
        config_menu.addAction(map_settings_action)
        
        # Add separator and additional options
        config_menu.addSeparator()
        
        # Theme selection submenu
        theme_menu = QMenu("Theme")
        theme_menu.setIcon(self.get_icon("theme-icon.png"))
        
        # Theme options
        system_theme_action = QAction("System Default", self)
        system_theme_action.triggered.connect(lambda: self.change_theme("system"))
        system_theme_action.setCheckable(True)
        
        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        light_theme_action.setCheckable(True)
        
        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        dark_theme_action.setCheckable(True)
        
        # Set the current theme as checked
        try:
            if hasattr(self, 'theme_manager'):
                current_theme = self.theme_manager.get_current_theme().value
                if current_theme == "system":
                    system_theme_action.setChecked(True)
                elif current_theme == "light":
                    light_theme_action.setChecked(True)
                elif current_theme == "dark":
                    dark_theme_action.setChecked(True)
        except Exception as e:
            logger.warning(f"Could not initialize theme selection: {e}")
            system_theme_action.setChecked(True)  # Default to system theme
        
        # Add theme actions to theme menu
        theme_menu.addAction(system_theme_action)
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)
        
        # Add theme menu to config menu
        config_menu.addMenu(theme_menu)
        
        # Set the menu on the config button
        self.config_button.setMenu(config_menu)
        
        # Connect the main button click
        self.config_button.clicked.connect(self.show_preferences_dialog)
        
        toolbar.addWidget(self.config_button)
        
        # Help section (new)
        toolbar.addSeparator()
        
        # Help action (new)
        help_action = self.create_action(
            "Help", 
            "help-icon.png", 
            "Show help (F1)",
            "F1", 
            self.show_help
        )
        toolbar.addAction(help_action)
        
        # About action (new)
        about_action = self.create_action(
            "About", 
            "about-icon.png", 
            "About CreepyAI",
            None, 
            self.show_about
        )
        toolbar.addAction(about_action)
        
        # Add toolbar to main window
        self.addToolBar(toolbar)
        return toolbar

    def create_action(self, text, icon_name, tooltip, shortcut=None, slot=None):
        """Create a QAction with the specified properties and connect to a slot"""
        action = QAction(text, self)
        
        # Set icon
        action.setIcon(self.get_icon(icon_name))
        
        # Set tooltip
        if shortcut:
            tooltip = f"{tooltip} ({shortcut})"
        action.setToolTip(tooltip)
        action.setStatusTip(tooltip)
        
        # Set shortcut if provided
        if shortcut:
            action.setShortcut(shortcut)
        
        # Connect to slot if provided
        if slot:
            action.triggered.connect(slot)
        
        return action

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
                "configure-icon.png": QStyle.SP_FileDialogDetailedView,
                "help-icon.png": QStyle.SP_DialogHelpButton,
                "about-icon.png": QStyle.SP_MessageBoxInformation,
                "refresh-icon.png": QStyle.SP_BrowserReload
            }
            
            # Get style from application
            style = QApplication.style()
            
            # Use appropriate standard icon or default
            if icon_name in fallbacks:
                return style.standardIcon(fallbacks[icon_name])
            else:
                return style.standardIcon(QStyle.SP_TitleBarMenuButton)
        
        return system_icon

    def import_data(self):
        """Import data from various sources"""
        try:
            from app.gui.ui.dialogs.import_dialog import ImportWizard
            wizard = ImportWizard(self)
            
            # Connect signal from wizard to handle results
            if hasattr(wizard, 'view_results_requested'):
                wizard.view_results_requested.connect(self.view_imported_results)
                
            wizard.exec_()
        except ImportError as e:
            logger.error(f"Could not open import dialog: {e}")
            QMessageBox.warning(self, "Import Not Available", 
                               "The import functionality is not available. Please check your installation.")

    def view_imported_results(self):
        """View results from import operation"""
        self.refresh_map()
        self.statusBar.showMessage("Showing imported data on map", 3000)

    def show_help(self):
        """Show the application help documentation"""
        # Check if help file exists locally
        help_file = os.path.join("docs", "index.html")
        if os.path.exists(help_file):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(help_file)))
        else:
            # Otherwise try to open online help
            QDesktopServices.openUrl(QUrl("https://example.com/creepyai/help"))

    def show_about(self):
        """Show the About dialog"""
        try:
            from app.gui.ui.dialogs.about_dialog import AboutDialog
            dialog = AboutDialog(self)
            dialog.exec_()
        except ImportError as e:
            logger.error(f"Could not open about dialog: {e}")
            QMessageBox.information(self, "About CreepyAI", 
                                  "CreepyAI - OSINT Location Intelligence Tool\n\nVersion 1.0.0")

    def show_preferences_dialog(self):
        """Show the application preferences dialog"""
        from app.gui.ui.dialogs.preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog(self)
        dialog.exec_()
        # Apply any changes that might affect the UI
        self.apply_preferences()
    
    def show_plugin_config_dialog(self):
        """Show the plugin configuration dialog"""
        from app.gui.ui.dialogs.plugin_config_dialog import PluginConfigDialog
        dialog = PluginConfigDialog(self.plugin_manager, self)
        dialog.exec_()
    
    def show_map_settings(self):
        """Show map settings dialog"""
        from app.gui.ui.dialogs.map_settings_dialog import MapSettingsDialog
        dialog = MapSettingsDialog(self.map_controller, self)
        if dialog.exec_():
            # Apply any map setting changes immediately
            self.map_controller.apply_settings()
    
    def change_theme(self, theme_name):
        """Change the application theme"""
        from app.core.theme_manager import Theme
        
        # Map string to Theme enum
        theme_map = {
            "system": Theme.SYSTEM,
            "light": Theme.LIGHT,
            "dark": Theme.DARK
        }
        
        if theme_name in theme_map:
            self.theme_manager.set_theme(theme_map[theme_name])
    
    def create_search_widget(self) -> QWidget:
        """Create and return the search widget with enhanced buttons"""
        search_widget = QWidget()
        layout = QVBoxLayout(search_widget)
        
        # Search input field with better styling
        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { background-color: #f8f8f8; border-radius: 5px; padding: 5px; }")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search locations or targets...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4a86e8;
            }
        """)
        # Add Enter key support
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        # Enhanced search button with icon and animation
        search_button = QPushButton("Search")
        search_button.setIcon(QIcon(os.path.join(self.icon_path, "search-icon.png")))
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5c94f0;
            }
            QPushButton:pressed {
                background-color: #3b77d9;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        search_button.setShortcut("Enter")
        search_button.setToolTip("Search for locations or targets (Enter)")
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(search_button)
        
        layout.addWidget(search_frame)
        
        # Search type options with improved toggle behavior
        search_type_frame = QFrame()
        search_type_frame.setStyleSheet("QFrame { margin-top: 10px; }")
        search_type_layout = QHBoxLayout(search_type_frame)
        search_type_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced Map Search toggle button
        self.map_search_btn = QPushButton("Search Map")
        self.map_search_btn.setIcon(QIcon(os.path.join(self.icon_path, "map-search-icon.png")))
        self.map_search_btn.setCheckable(True)
        self.map_search_btn.setChecked(True)
        self.map_search_btn.setToolTip("Search for locations on the map")
        self.map_search_btn.setCursor(Qt.PointingHandCursor)
        self.map_search_btn.setStyleSheet(self._get_toggle_button_style())
        self.map_search_btn.clicked.connect(self.toggle_search_type)
        search_type_layout.addWidget(self.map_search_btn)
        
        # Enhanced Target Search toggle button
        self.target_search_btn = QPushButton("Search Targets")
        self.target_search_btn.setIcon(QIcon(os.path.join(self.icon_path, "target-icon.png")))
        self.target_search_btn.setCheckable(True)
        self.target_search_btn.setToolTip("Search for targets by name")
        self.target_search_btn.setCursor(Qt.PointingHandCursor)
        self.target_search_btn.setStyleSheet(self._get_toggle_button_style())
        self.target_search_btn.clicked.connect(self.toggle_search_type)
        search_type_layout.addWidget(self.target_search_btn)
        
        layout.addWidget(search_type_frame)
        
        # Search results label with better styling
        self.results_label = QLabel("Enter a search term above to find locations or targets")
        self.results_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border-radius: 3px;
                padding: 8px;
                margin-top: 10px;
            }
        """)
        self.results_label.setWordWrap(True)
        layout.addWidget(self.results_label)
        
        # Results actions with enhanced buttons
        actions_frame = QFrame()
        actions_frame.setStyleSheet("QFrame { margin-top: 15px; }")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced Clear Results button
        clear_results_btn = QPushButton("Clear Results")
        clear_results_btn.setIcon(QIcon(os.path.join(self.icon_path, "clear-icon.png")))
        clear_results_btn.setToolTip("Clear search results and reset map")
        clear_results_btn.setCursor(Qt.PointingHandCursor)
        clear_results_btn.setStyleSheet(self._get_secondary_button_style())
        clear_results_btn.clicked.connect(self.clear_search_results)
        actions_layout.addWidget(clear_results_btn)
        
        # Enhanced Export Results button
        export_results_btn = QPushButton("Export Results")
        export_results_btn.setIcon(QIcon(os.path.join(self.icon_path, "export-results-icon.png")))
        export_results_btn.setToolTip("Export search results to a file")
        export_results_btn.setCursor(Qt.PointingHandCursor)
        export_results_btn.setStyleSheet(self._get_secondary_button_style())
        export_results_btn.clicked.connect(self.export_search_results)
        actions_layout.addWidget(export_results_btn)
        
        layout.addWidget(actions_frame)
        
        # Add stretching space
        layout.addStretch()
        
        return search_widget
    
    def create_filters_widget(self) -> QWidget:
        """Create and return the filters widget with enhanced buttons"""
        filters_widget = QWidget()
        layout = QVBoxLayout(filters_widget)
        
        # Date range filter with improved styling
        date_frame = QFrame()
        date_frame.setStyleSheet("QFrame { background-color: #f8f8f8; border-radius: 5px; padding: 10px; }")
        date_layout = QVBoxLayout(date_frame)
        
        # Add a title with better styling
        title_label = QLabel("Date Range Filter")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        date_layout.addWidget(title_label)
        
        # From date with better styling
        from_frame = QFrame()
        from_layout = QHBoxLayout(from_frame)
        from_layout.setContentsMargins(0, 0, 0, 0)
        
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-weight: bold;")
        from_layout.addWidget(from_label)
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addYears(-1))
        self.from_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 4px;
                background: white;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
            }
        """)
        from_layout.addWidget(self.from_date)
        date_layout.addWidget(from_frame)
        
        # To date with better styling
        to_frame = QFrame()
        to_layout = QHBoxLayout(to_frame)
        to_layout.setContentsMargins(0, 0, 0, 0)
        
        to_label = QLabel("To:")
        to_label.setStyleSheet("font-weight: bold;")
        to_layout.addWidget(to_label)
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 4px;
                background: white;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
            }
        """)
        to_layout.addWidget(self.to_date)
        date_layout.addWidget(to_frame)
        
        # Enhanced Apply button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.setIcon(QIcon(os.path.join(self.icon_path, "filter-icon.png")))
        apply_btn.setToolTip("Apply date filters to the map")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #5c94f0;
            }
            QPushButton:pressed {
                background-color: #3b77d9;
            }
        """)
        apply_btn.clicked.connect(self.apply_filters)
        date_layout.addWidget(apply_btn)
        
        layout.addWidget(date_frame)
        
        # Add stretching space
        layout.addStretch()
        
        return filters_widget
    
    def setup_signals(self):
        """Connect signals and slots"""
        # Connect map controller signals
        if self.map_controller:
            self.map_controller.markersUpdated.connect(self.update_marker_count)
            self.map_controller.mapLayerChanged.connect(self.update_layer_selection)
    
    @pyqtSlot(int)
    def update_marker_count(self, count):
        """Update the status bar with marker count"""
        self.status_label.setText(f"Displaying {count} locations on map")
    
    @pyqtSlot(str)
    def update_layer_selection(self, layer_name):
        """Update UI when map layer changes"""
        # Update combo box to match map state
        if self.map_layer_combo.currentText() != layer_name:
            self.map_layer_combo.setCurrentText(layer_name)

    def toggle_search_type(self):
        """Toggle between map search and target search"""
        if self.sender() is self.map_search_btn:
            self.map_search_btn.setChecked(True)
            self.target_search_btn.setChecked(False)
        else:
            self.map_search_btn.setChecked(False) 
            self.target_search_btn.setChecked(True)
    
    def perform_search(self):
        """Perform search based on current mode with improved feedback"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.results_label.setText("⚠️ Please enter a search term")
            self.results_label.setStyleSheet("QLabel { background-color: #fff3cd; color: #856404; border-radius: 3px; padding: 8px; }")
            QApplication.beep()  # Provide audible feedback
            return
        
        # Show searching feedback
        self.results_label.setText("🔍 Searching...")
        self.results_label.setStyleSheet("QLabel { background-color: #f0f0f0; border-radius: 3px; padding: 8px; }")
        QApplication.processEvents()  # Update UI immediately
        
        try:
            if self.map_search_btn.isChecked():
                # Search on map
                count = self.map_controller.search_map(search_term)
                if count > 0:
                    self.results_label.setText(f"✅ Found {count} locations matching '{search_term}'")
                    self.results_label.setStyleSheet("QLabel { background-color: #d4edda; color: #155724; border-radius: 3px; padding: 8px; }")
                else:
                    self.results_label.setText(f"ℹ️ No locations found matching '{search_term}'")
                    self.results_label.setStyleSheet("QLabel { background-color: #d1ecf1; color: #0c5460; border-radius: 3px; padding: 8px; }")
            else:
                # Search for targets
                self.search_results = self.map_controller.search_for_targets(search_term)
                if self.search_results:
                    self.results_label.setText(f"✅ Found {len(self.search_results)} potential targets matching '{search_term}'")
                    self.results_label.setStyleSheet("QLabel { background-color: #d4edda; color: #155724; border-radius: 3px; padding: 8px; }")
                else:
                    self.results_label.setText(f"ℹ️ No targets found matching '{search_term}'")
                    self.results_label.setStyleSheet("QLabel { background-color: #d1ecf1; color: #0c5460; border-radius: 3px; padding: 8px; }")
        except Exception as e:
            # Improve error handling with better feedback
            error_msg = str(e)
            self.results_label.setText(f"❌ Error during search: {error_msg}")
            self.results_label.setStyleSheet("QLabel { background-color: #f8d7da; color: #721c24; border-radius: 3px; padding: 8px; }")
            logger.error(f"Search error: {error_msg}")

    def clear_search_results(self):
        """Clear search results and reset map with visual feedback"""
        self.search_input.clear()
        self.results_label.setText("Ready for new search")
        self.results_label.setStyleSheet("QLabel { background-color: #f0f0f0; border-radius: 3px; padding: 8px; }")
        self.map_controller.clear_search()
        self.search_results = []
        self.status_label.setText("Search results cleared")
        
        # Momentarily highlight the status label
        original_style = self.status_label.styleSheet()
        self.status_label.setStyleSheet("color: #4a86e8; font-weight: bold;")
        
        # Reset to original style after brief delay
        QTimer.singleShot(1500, lambda: self.status_label.setStyleSheet(original_style))

    def export_search_results(self):
        """Export search results to a file with improved error handling and feedback"""
        has_results = bool(self.search_results) if self.target_search_btn.isChecked() else bool(self.map_controller.markers)
        
        if not has_results:
            QMessageBox.information(self, "Export Results", "No results to export")
            return
        
        # Set up filters based on search type
        if self.map_search_btn.isChecked():
            filters = "JSON Files (*.json);;CSV Files (*.csv);;KML Files (*.kml);;All Files (*)"
        else:
            filters = "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Search Results", "", filters
        )
        
        if not filename:
            return  # User canceled
            
        # Show progress indication
        self.status_label.setText("Exporting results...")
        QApplication.processEvents()
        
        try:
            import json
            import csv
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    if self.map_search_btn.isChecked():
                        json.dump(self.map_controller.markers, f, indent=2)
                    else:
                        json.dump(self.search_results, f, indent=2)
            elif filename.endswith('.csv'):
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    if self.map_search_btn.isChecked():
                        # Export map markers
                        writer = csv.writer(f)
                        writer.writerow(['Latitude', 'Longitude', 'Title', 'Content', 'Timestamp', 'Source'])
                        for marker in self.map_controller.markers:
                            writer.writerow([
                                marker['lat'], marker['lng'], 
                                marker.get('title', ''), 
                                marker.get('content', ''), 
                                marker.get('timestamp', ''), 
                                marker.get('source', '')
                            ])
                    else:
                        # Export targets
                        writer = csv.writer(f)
                        writer.writerow(['Target ID', 'Target Name', 'Plugin'])
                        for target in self.search_results:
                            writer.writerow([
                                target.get('targetId', ''), 
                                target.get('targetName', ''), 
                                target.get('pluginName', '')
                            ])
            elif filename.endswith('.kml') and self.map_search_btn.isChecked():
                # Export as KML only for map markers
                self._export_as_kml(filename, self.map_controller.markers)
            else:
                raise ValueError(f"Unsupported file format: {os.path.splitext(filename)[1]}")
            
            self.status_label.setText(f"Results exported to {os.path.basename(filename)}")
            QMessageBox.information(self, "Export Results", 
                                  f"Results exported successfully to:\n{filename}")
        
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            QMessageBox.critical(self, "Export Error", 
                               f"Error exporting results: {str(e)}")
            self.status_label.setText("Export failed")

    def _export_as_kml(self, filename: str, markers: list) -> None:
        """Export map markers as KML file"""
        try:
            import simplekml
            kml = simplekml.Kml()
            
            # Add markers as placemarks
            for marker in markers:
                placemark = kml.newpoint(
                    name=marker.get('title', 'Location'),
                    description=marker.get('content', ''),
                    coords=[(marker['lng'], marker['lat'])]
                )
                
                # Add timestamp if available
                if 'timestamp' in marker and marker['timestamp']:
                    placemark.timestamp.when = marker['timestamp']
                
                # Add style (could be enhanced with source-specific styling)
                placemark.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
                
            kml.save(filename)
        except ImportError:
            raise ImportError("SimplKML package is required for KML export. Install with: pip install simplekml")
    
    def apply_filters(self):
        """Apply date and other filters to the map"""
        # Convert QDate to Python datetime
        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()
        
        # Add time components for full day range
        from_datetime = datetime.datetime.combine(from_date, datetime.time.min)
        to_datetime = datetime.datetime.combine(to_date, datetime.time.max)
        
        # Update map controller date range
        self.map_controller.set_date_range(from_datetime, to_datetime)
        
        # Update status
        self.status_label.setText(f"Filters applied: {from_date} to {to_date}")
    
    def refresh_map(self):
        """Refresh map data"""
        self.map_controller.update_map_markers()
        self.status_label.setText("Map refreshed")
    
    def new_project(self):
        """Create a new project"""
        # Implementation would clear current data and start fresh
        self.statusBar.showMessage("New project created", 3000)
    
    def open_project(self):
        """Open an existing project"""
        # Implementation would load project data
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "CreepyAI Projects (*.cai);;All Files (*)"
        )
        if filename:
            self.statusBar.showMessage(f"Opened project: {filename}", 3000)
    
    def save_project(self):
        """Save the current project"""
        # Implementation would save project data
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "CreepyAI Projects (*.cai);;All Files (*)"
        )
        if filename:
            self.statusBar.showMessage(f"Project saved: {filename}", 3000)
    
    def export_data(self):
        """Export data to file"""
        # Implementation would export all current map data
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            self.statusBar.showMessage(f"Data exported to: {filename}", 3000)
    
    def change_map_layer(self, layer_name):
        """Change the map base layer"""
        if self.map_controller:
            success = self.map_controller.set_map_layer(layer_name)
            if success:
                self.status_label.setText(f"Map layer changed to: {layer_name}")
                
                # Show keyboard shortcut tip
                shortcuts = self.map_controller.get_keyboard_shortcuts_help()
                for shortcut, description in shortcuts.items():
                    if layer_name in description:
                        self.map_controller.show_map_tooltip(f"Tip: {shortcut} keyboard shortcut toggles this view")
                        break

    def show_map_help(self):
        """Show help about map controls"""
        help_text = """<b>Map Controls</b><br><br>
        <b>Map Types:</b>
        • Change map type using the dropdown in toolbar
        • Use the map panel in the bottom left of the map
        • Use keyboard shortcuts: Ctrl+1 through Ctrl+4<br><br>
        <b>Navigation:</b>
        • Pan: Click and drag the map
        • Zoom: Use scroll wheel or +/- buttons
        • Reset view: Double-click on the map<br><br>
        <b>Map Controls:</b>
        • The map type selector can be dragged to any position
        • Click layer control in top-right to toggle marker visibility
        """
        
        QMessageBox.information(self, "Map Controls Help", help_text)
    
    def _get_toggle_button_style(self) -> str:
        """Get consistent style for toggle buttons"""
        return """
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px 10px;
                background-color: #f5f5f5;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
            QPushButton:checked {
                background-color: #4a86e8;
                color: white;
                border-color: #3a77d9;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

    def _get_secondary_button_style(self) -> str:
        """Get consistent style for secondary buttons"""
        return """
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px 10px;
                background-color: #f5f5f5;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #aaa;
                border-color: #ddd;
            }
        """
