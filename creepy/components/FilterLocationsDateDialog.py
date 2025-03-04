#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from ui.FilterLocationsDateDialog import Ui_FilterLocationsDateDialog
from yapsy.PluginManager import PluginManagerSingleton

class FilterLocationsDateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FilterLocationsDateDialog()
        self.ui.setupUi(self)
        self.setupConnections()
        self.setupPlugins()

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