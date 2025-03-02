#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QObject, pyqtSlot
from ui.FilterLocationsPointDialogUI import Ui_FilterLocationsPointDialog

class PointReceiver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    @pyqtSlot(float, float)
    def setPoint(self, lat, lng):
        self.lat = lat
        self.lng = lng

class FilterLocationsPointDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_FilterLocationsPointDialog()
        self.ui.setupUi(self)
        
        # Set defaults
        self.ui.radiusSpinBox.setValue(5)  # Default 5 km radius
        self.unit = 'km'  # Default unit is km
        
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
    
    def pyObj(self):
        """Returns a Python object that can be used with JavaScript"""
        self.pointReceiver = PointReceiver()
        return self.pointReceiver
    
    def onUnitChanged(self, text):
        """Called when the radius unit is changed"""
        self.unit = text
        # Adjust the maximum value based on the unit
        if text == 'km':
            self.ui.radiusSpinBox.setMaximum(1000)
        else:
            self.ui.radiusSpinBox.setMaximum(100000)

