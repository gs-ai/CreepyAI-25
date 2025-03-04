#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractListModel, Qt
from PyQt5.QtGui import QPixmap, QIcon
import os

class ProjectWizardPluginListModel(QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(ProjectWizardPluginListModel, self).__init__(parent)
        self.plugins = plugins
        self.checkedPlugins = set()
    
    def rowCount(self, index):
        return len(self.plugins)
    
    def data(self, index, role):
        if not index.isValid():
            return None
            
        plugin = self.plugins[index.row()][0]
        
        if role == Qt.DisplayRole:
            return plugin.name
        elif role == Qt.DecorationRole:
            picturePath = os.path.join(os.getcwd(), 'plugins', plugin.plugin_object.name, 'logo.png')
            if picturePath and os.path.exists(picturePath):
                pixmap = QPixmap(picturePath)
                return QIcon(pixmap.scaled(30, 30, Qt.IgnoreAspectRatio, Qt.FastTransformation))
            else:
                pixmap = QPixmap(':/creepy/generic_plugin')
                return QIcon(pixmap.scaled(30, 30, Qt.IgnoreAspectRatio))
        elif role == Qt.CheckStateRole:
            if plugin:
                return Qt.Checked if plugin.name in self.checkedPlugins else Qt.Unchecked
                
        return None
                  
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            plugin = self.plugins[index.row()][0]
            if value == Qt.Checked:
                self.checkedPlugins.add(plugin.name)
            else:
                self.checkedPlugins.discard(plugin.name)
            return True
        return super().setData(index, value, role)
                  
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractListModel.flags(self, index)|Qt.ItemIsUserCheckable)