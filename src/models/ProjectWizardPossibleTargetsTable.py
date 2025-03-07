#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractTableModel, Qt

class ProjectWizardPossibleTargetsTable(QAbstractTableModel):
    """Table model for possible targets in the project wizard"""
    
    def __init__(self, targets, parent=None):
        super(ProjectWizardPossibleTargetsTable, self).__init__(parent)
        self.targets = targets
        self.headers = ["Name", "Plugin", "Status"]
    
    def rowCount(self, parent=None):
        return len(self.targets)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        target = self.targets[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:  # Name
                return target.get("name", "")
            elif column == 1:  # Plugin
                return target.get("plugin", "")
            elif column == 2:  # Status
                return target.get("status", "")
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None