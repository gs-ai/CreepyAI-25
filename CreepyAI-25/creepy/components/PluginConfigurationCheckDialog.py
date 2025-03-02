#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from ui.PluginConfigCheckdialog import Ui_checkPluginConfigurationDialog
from yapsy.PluginManager import PluginManagerSingleton

class PluginConfigurationCheckdialog(QDialog):
    """
    Loads the Plugin Configuration Check Dialog that provides information indicating
    if a plugin is configured or not
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_checkPluginConfigurationDialog()
        try:
            self.ui.setupUi(self)
        except Exception as e:
            print(f"Error setting up UI: {e}")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupPlugins()

    def setupPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error setting up plugins: {e}")
