#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QDir

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the UI file
try:
    from CreepyUI import Ui_CreepyMainWindow
except ImportError:
    from ui.CreepyUI import Ui_CreepyMainWindow

class CreepyAIPreview(QMainWindow):
    """Preview class for CreepyAI GUI interface"""
    
    def __init__(self):
        super(CreepyAIPreview, self).__init__()
        self.ui = Ui_CreepyMainWindow()
        self.ui.setupUi(self)
        
        # Set up basic window properties
        self.setWindowTitle("CreepyAI - GUI Preview")
        
        # Load CSS style if available
        css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'include', 'style.qss')
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                self.setStyleSheet(f.read())
        
        # Connect the menu actions
        self.ui.actionPluginsConfiguration.triggered.connect(self.show_plugins_config)
        self.ui.actionAbout.triggered.connect(self.show_about)
        self.ui.actionCheckUpdates.triggered.connect(self.check_updates)
        self.ui.actionExportKML.triggered.connect(self.export_kml)
        self.ui.actionExportCSV.triggered.connect(self.export_csv)
        
        # Set up the map view with blank page
        self.ui.mapWebView.load('about:blank')
        
        # Show welcome message
        self.show_welcome()
    
    def show_welcome(self):
        """Show welcome message"""
        QMessageBox.information(self, "CreepyAI Preview Mode",
                               "This is a preview of the CreepyAI GUI interface.\n\n"
                               "Feel free to explore the interface, but functionality "
                               "is limited in preview mode.")
    
    def show_plugins_config(self):
        """Show plugins configuration dialog"""
        QMessageBox.information(self, "Plugins Configuration",
                               "The plugins configuration dialog would open here.\n\n"
                               "In preview mode, this functionality is disabled.")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About CreepyAI",
                         "<h2>CreepyAI v2.5.0</h2>"
                         "<p>A geolocation OSINT tool with AI capabilities.</p>"
                         "<p>License: MIT</p>")
    
    def check_updates(self):
        """Check for updates"""
        QMessageBox.information(self, "Update Check",
                               "Checking for updates is disabled in preview mode.")
    
    def export_kml(self):
        """Export to KML"""
        QMessageBox.information(self, "Export KML",
                               "KML export functionality is disabled in preview mode.\n\n"
                               "In full mode, this would export location data to KML format "
                               "for use in Google Earth and other GIS applications.")
    
    def export_csv(self):
        """Export to CSV"""
        QMessageBox.information(self, "Export CSV",
                               "CSV export functionality is disabled in preview mode.\n\n"
                               "In full mode, this would export location data to CSV format.")

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("CreepyAI")
    app.setOrganizationName("CreepyAI")
    
    # Print instructions
    print("CreepyAI GUI Preview")
    print("--------------------")
    print("This is a preview of the CreepyAI GUI interface.")
    print("Feel free to interact with all elements to test functionality.")
    print("Note: Most features are disabled in preview mode.")
    
    # Create and show the window
    window = CreepyAIPreview()
    window.show()
    
    # Enter the Qt main loop
    sys.exit(app.exec_())
