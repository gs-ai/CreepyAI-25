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

# Import UI components - try multiple paths to make it work
try:
    # Try directly from app.gui.ui
    from app.gui.ui.about_dialog import AboutDialog
    from app.gui.ui.plugin_config_dialog import PluginsConfigDialog
    from app.gui.ui.settings_dialog import SettingsDialog
except ImportError:
    try:
        # Add gui directory to path
        gui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, gui_dir)
        from ui.about_dialog import AboutDialog
        from ui.plugin_config_dialog import PluginsConfigDialog
        from ui.settings_dialog import SettingsDialog
    except ImportError:
        print("Creating mock UI classes as imports failed")
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
