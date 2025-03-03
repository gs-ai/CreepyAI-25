#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant

class ProjectWizardSelectedTargetsTable(QAbstractTableModel):
    """Model for displaying selected targets in the project wizard"""
    
    def __init__(self, parent=None):
        super(ProjectWizardSelectedTargetsTable, self).__init__(parent)
        
        self.targets = []  # List of target dictionaries
        self.headers = ["Name", "Username", "Platform"]
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows in the model"""
        if parent.isValid():
            return 0
        return len(self.targets)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns in the model"""
        if parent.isValid():
            return 0
        return 3
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given role and index"""
        if not index.isValid() or index.row() >= len(self.targets):
            return QVariant()
        
        target = self.targets[index.row()]
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return target.get("name", "")
            elif index.column() == 1:
                return target.get("username", "")
            elif index.column() == 2:
                return target.get("platform", "")
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data for the given role, section and orientation"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        
        return QVariant()