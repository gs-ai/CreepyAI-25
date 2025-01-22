#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QObject, pyqtSlot
from ui.FilterLocationsPointDialog import Ui_FilteLocationsPointDialog
from yapsy.PluginManager import PluginManagerSingleton

class FilterLocationsPointDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FilteLocationsPointDialog()
        self.ui.setupUi(self)
        self.unit = 'km'
        self.setupPlugins()

    def setupPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error setting up plugins: {e}")
    
    def onUnitChanged(self, index):
        if index in ['km', 'miles']:
            self.unit = index
        else:
            self.unit = 'km'  # default to km if invalid index

    class pyObj(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.selectedLat = None
            self.selectedLng = None
        
        @pyqtSlot(str)
        def setLatLng(self, latlng):
            try:
                lat, lng = latlng.replace('(', '').replace(')', '').split(',')
                self.lat = float(lat)
                self.lng = float(lng)
            except ValueError:
                self.lat = None
                self.lng = None
                print("Invalid latitude and longitude format")

