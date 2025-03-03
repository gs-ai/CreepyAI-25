#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QVariant

class ProjectWizardPluginListModel(QAbstractListModel):
    """Model for displaying and selecting plugins in the project wizard"""
    
    def __init__(self, plugin_manager, parent=None):
        super(ProjectWizardPluginListModel, self).__init__(parent)
        
        self.plugin_manager = plugin_manager
        self.plugins = plugin_manager.get_input_plugins()
        self.selected_plugins = set()  # Set of selected plugin names
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows in the model"""
        if parent.isValid():
            return 0
        return len(self.plugins)
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given role and index"""
        if not index.isValid() or index.row() >= len(self.plugins):
            return QVariant()
        
        plugin = self.plugins[index.row()]
        
        if role == Qt.DisplayRole:
            return plugin.name
        elif role == Qt.ToolTipRole:
            return plugin.description
        elif role == Qt.CheckStateRole:
            return Qt.Checked if plugin.name in self.selected_plugins else Qt.Unchecked
        
        return QVariant()
    
    def flags(self, index):
        """Return item flags for the given index"""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
    
    def setData(self, index, value, role=Qt.EditRole):
        """Set data for the given index and role"""
        if not index.isValid() or index.row() >= len(self.plugins):
            return False
        
        if role == Qt.CheckStateRole:
            plugin = self.plugins[index.row()]
            
            if value == Qt.Checked:
                self.selected_plugins.add(plugin.name)
            else:
                self.selected_plugins.discard(plugin.name)
            
            self.dataChanged.emit(index, index)
            return True
        
        return False
    
    def get_selected_plugins(self):
        """Return list of selected plugin names"""
        return list(self.selected_plugins)
    
    def select_all(self):
        """Select all plugins"""
        self.selected_plugins = set(plugin.name for plugin in self.plugins)
        self.dataChanged.emit(self.index(0, 0), self.index(len(self.plugins) - 1, 0))
    
    def deselect_all(self):
        """Deselect all plugins"""
        self.selected_plugins.clear()
        self.dataChanged.emit(self.index(0, 0), self.index(len(self.plugins) - 1, 0))