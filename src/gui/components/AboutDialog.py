#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from ui.AboutDialog import Ui_aboutDialog
from yapsy.PluginManager import PluginManagerSingleton

class AboutDialog(QDialog):
    """Dialog showing information about the application."""
    
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_aboutDialog()
        self.ui.setupUi(self)
        self.setupConnections()
        self.setupPlugins()
        
        # Set version from the application
        try:
            if parent and hasattr(parent, 'version'):
                self.ui.versionLabel.setText(f"Version {parent.version}")
        except Exception as e:
            pass  # Ignore version setting errors
        
        # Connect hyperlinks to open in browser
        self.ui.aboutText.setOpenExternalLinks(True)

    def setupConnections(self):
        try:
            # Add any signal-slot connections here
            pass
        except Exception as e:
            print(f"Error setting up connections: {str(e)}")

    def setupPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error setting up plugins: {e}")