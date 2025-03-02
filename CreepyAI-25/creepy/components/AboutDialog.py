#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from ui.AboutDialogUI import Ui_AboutDialog

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)

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