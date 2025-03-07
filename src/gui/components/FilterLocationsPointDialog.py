#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QObject, pyqtSlot
from yapsy.PluginManager import PluginManagerSingleton

class PyObj(QObject):
    """Object to communicate with JavaScript"""
    def __init__(self, parent=None):
        super(PyObj, self).__init__(parent)
        self.lat = None
        self.lng = None
    
    @pyqtSlot(float, float)
    def setCoordinates(self, lat, lng):
        """Slot to receive coordinates from JavaScript"""
        self.lat = lat
        self.lng = lng

class Ui_FilterLocationsPointDialog(object):
    """UI for the Filter Locations by Point dialog"""
    
    def setupUi(self, FilterLocationsPointDialog):
        """Setup the UI elements"""
        FilterLocationsPointDialog.setObjectName("FilterLocationsPointDialog")
        FilterLocationsPointDialog.resize(800, 600)
        FilterLocationsPointDialog.setWindowTitle("Filter Locations by Distance")
        
        # Main layout
        self.mainLayout = QVBoxLayout(FilterLocationsPointDialog)
        self.mainLayout.setObjectName("mainLayout")
        
        # Instructions label
        self.instructionsLabel = QLabel("Click on the map to select a point, then set the radius to filter locations.", FilterLocationsPointDialog)
        self.instructionsLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.instructionsLabel)
        
        # Web view for the map
        self.webView = QWebEngineView(FilterLocationsPointDialog)
        self.webView.setObjectName("webView")
        self.webView.setMinimumSize(780, 450)
        self.mainLayout.addWidget(self.webView)
        
        # Radius controls
        self.radiusLayout = QHBoxLayout()
        self.radiusLabel = QLabel("Radius:", FilterLocationsPointDialog)
        self.radiusSpinBox = QSpinBox(FilterLocationsPointDialog)
        self.radiusSpinBox.setObjectName("radiusSpinBox")
        self.radiusSpinBox.setRange(1, 100000)
        self.radiusSpinBox.setValue(10)
        
        self.radiusUnitComboBox = QComboBox(FilterLocationsPointDialog)
        self.radiusUnitComboBox.setObjectName("radiusUnitComboBox")
        
        self.radiusLayout.addWidget(self.radiusLabel)
        self.radiusLayout.addWidget(self.radiusSpinBox)
        self.radiusLayout.addWidget(self.radiusUnitComboBox)
        self.radiusLayout.addStretch()
        
        self.mainLayout.addLayout(self.radiusLayout)
        
        # Add OK/Cancel buttons
        from PyQt5.QtWidgets import QDialogButtonBox
        from PyQt5.QtCore import Qt
        
        self.buttonBox = QDialogButtonBox(FilterLocationsPointDialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.mainLayout.addWidget(self.buttonBox)
        
        # Connect signals
        self.buttonBox.accepted.connect(FilterLocationsPointDialog.accept)
        self.buttonBox.rejected.connect(FilterLocationsPointDialog.reject)

class FilterLocationsPointDialog(QDialog):
    """Dialog for filtering locations by distance from a point"""
    
    def __init__(self, parent=None):
        super(FilterLocationsPointDialog, self).__init__(parent)
        self.ui = Ui_FilterLocationsPointDialog()
        self.ui.setupUi(self)
        self.unit = 'km'  # Default unit
        self.setupPlugins()
        
        # Create object for JavaScript communication
        self._pyObj = PyObj()
    
    def pyObj(self):
        """Return the Python object for JavaScript communication"""
        return self._pyObj
    
    def onUnitChanged(self, text):
        """Handle unit change"""
        self.unit = text
        if text == 'km':
            self.ui.radiusSpinBox.setRange(1, 1000)
            self.ui.radiusSpinBox.setValue(10)
        else:  # 'm'
            self.ui.radiusSpinBox.setRange(10, 100000)
            self.ui.radiusSpinBox.setValue(1000)

    def setupPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error setting up plugins: {e}")

