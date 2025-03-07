#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QColor

class ProjectWizardSelectedTargetsTable(QAbstractTableModel):
    """
    Model for displaying selected targets in the project wizard
    """

    def __init__(self, selectedTargets, parent=None):
        super(ProjectWizardSelectedTargetsTable, self).__init__(parent)
        self.selectedTargets = selectedTargets
        self.headers = ["Plugin", "Name", "Username", "ID", "Selected"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.selectedTargets)

    def columnCount(self, parent=QModelIndex()):
        return 5  # Plugin, Name, Username, ID, Selected

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.selectedTargets)):
            return None

        target = self.selectedTargets[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return target.get('pluginName', '')
            elif index.column() == 1:
                return target.get('targetName', '')
            elif index.column() == 2:
                return target.get('targetUser', '')
            elif index.column() == 3:
                return target.get('targetId', '')

        elif role == Qt.CheckStateRole:
            if index.column() == 4:
                return Qt.Checked if target.get('selected', True) else Qt.Unchecked
        
        # Optional: Add background colors for different plugins
        elif role == Qt.BackgroundRole:
            plugin = target.get('pluginName', '')
            if plugin == 'DummyPlugin':
                return QColor(240, 240, 255)  # Light blue for dummy targets
        
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == 4:
            self.selectedTargets[index.row()]['selected'] = (value == Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 4:  # Make last column checkable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
