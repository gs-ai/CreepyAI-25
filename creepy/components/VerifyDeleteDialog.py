#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from ui.VerifyDeleteDialog import Ui_verifyDeleteDialog
from yapsy.PluginManager import PluginManagerSingleton

class VerifyDeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_verifyDeleteDialog()
        try:
            self.ui.setupUi(self)
        except Exception as e:
            print(f"Error setting up UI: {e}")
        self.setupPlugins()

    def setupPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error setting up plugins: {e}")
