#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractListModel, Qt
from PyQt5.QtGui import QPixmap, QIcon
import os

class PluginConfigurationListModel(QAbstractListModel):
    def __init__(self, plugins, parent=None):
        super(PluginConfigurationListModel, self).__init__(parent)
        self.plugins = []
        self.pluginList = plugins
    
    def checkPluginConfiguration(self):
        self.plugins = []
        for plugin in self.pluginList:
            self.plugins.append((plugin, True))
        
    def rowCount(self, index):
        return len(self.plugins)
    
    def data(self, index, role):
        if not index.isValid():
            return None
            
        pluginListItem = self.plugins[index.row()]
        
        if role == Qt.DisplayRole:
            return pluginListItem[0].name
        elif role == Qt.DecorationRole:
            picturePath = os.path.join(os.getcwd(), 'plugins', pluginListItem[0].plugin_object.name, 'logo.png')
            if picturePath and os.path.exists(picturePath):
                pixmap = QPixmap(picturePath)
                return QIcon(pixmap)
            else:
                pixmap = QPixmap(':/creepy/folder')
                return QIcon(pixmap)
                
        return None