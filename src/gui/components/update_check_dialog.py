#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QDialogButtonBox

class UpdateCheckDialog(QDialog):
    """Dialog to display update check results."""
    
    def __init__(self, parent=None):
        super(UpdateCheckDialog, self).__init__(parent)
        self.setWindowTitle("Check for Updates")
        self.setupUI()
        
    def setupUI(self):
        # Create layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # Title label
        self.titleLabel = QLabel("Updates", self)
        layout.addWidget(self.titleLabel)
        
        # Versions table
        self.versionsTableWidget = QTableWidget(1, 5, self)
        self.versionsTableWidget.setHorizontalHeaderLabels(('', 'Component', 'Status', 'Installed', 'Available'))
        self.versionsTableWidget.verticalHeader().setVisible(False)
        self.versionsTableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.versionsTableWidget)
        
        # Results label
        self.dlNewVersionLabel = QLabel("", self)
        self.dlNewVersionLabel.setOpenExternalLinks(True)
        layout.addWidget(self.dlNewVersionLabel)
        
        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)
        
        # Set dialog size
        self.resize(500, 250)
