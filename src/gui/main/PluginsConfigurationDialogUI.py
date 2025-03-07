from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PluginsConfigurationDialog(object):
    def setupUi(self, PluginsConfigurationDialog):
        PluginsConfigurationDialog.setObjectName("PluginsConfigurationDialog")
        PluginsConfigurationDialog.resize(800, 600)
        PluginsConfigurationDialog.setWindowTitle("Plugins Configuration")
        
        # Main layout
        self.mainLayout = QtWidgets.QHBoxLayout(PluginsConfigurationDialog)
        
        # Plugin list view
        self.PluginsList = QtWidgets.QListView()
        self.PluginsList.setObjectName("PluginsList")
        self.PluginsList.setMaximumWidth(200)
        self.mainLayout.addWidget(self.PluginsList)
        
        # Right side layout
        self.rightLayout = QtWidgets.QVBoxLayout()
        
        # Button layout
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.ButtonSave = QtWidgets.QPushButton("Save")
        self.ButtonClose = QtWidgets.QPushButton("Close")
        self.buttonLayout.addWidget(self.ButtonSave)
        self.buttonLayout.addWidget(self.ButtonClose)
        
        # Add to right layout
        self.rightLayout.addStretch(1)
        self.rightLayout.addLayout(self.buttonLayout)
        
        self.mainLayout.addLayout(self.rightLayout)
        
        # Connect buttons
        self.ButtonClose.clicked.connect(PluginsConfigurationDialog.reject)
