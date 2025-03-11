#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QIcon, QColor

class ProjectWizardPluginListModel(QAbstractTableModel):
    """
    Model for displaying plugins in the project wizard.
    """
    
    def __init__(self, plugins, parent=None):
        super(ProjectWizardPluginListModel, self).__init__(parent)
        self.plugins = plugins
        self.headers = ["Plugin Name", "Description", "Status"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.plugins)

    def columnCount(self, parent=QModelIndex()):
        return 3  # Plugin name, description, enabled status

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.plugins)):
            return None

        plugin = self.plugins[index.row()]
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return plugin.name
            elif index.column() == 1:
                return plugin.description
            elif index.column() == 2:
                # Check if plugin is configured
                try:
                    result, message = plugin.plugin_object.isConfigured()
                    return "Ready" if result else "Not configured"
                except Exception as e:
                    return "Error"
        
        elif role == Qt.BackgroundRole:
            if index.column() == 2:
                try:
                    result, message = plugin.plugin_object.isConfigured()
                    return QColor(200, 255, 200) if result else QColor(255, 200, 200)
                except Exception:
                    return QColor(255, 200, 200)
                    
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                return Qt.Checked if getattr(plugin, 'selected', False) else Qt.Unchecked
        
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == 0:
            plugin = self.plugins[index.row()]
            plugin.selected = (value == Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 0:  # Make first column checkable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal and section < len(self.headers):
            return self.headers[section]
        return None
