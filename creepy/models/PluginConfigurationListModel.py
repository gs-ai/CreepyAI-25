#!/usr/bin/python
# -*- coding: utf-8 -*-
<<<<<<< HEAD
from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex
from PyQt5.QtGui import QPixmap, QIcon, QColor, QBrush
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

class PluginConfigurationListModel(QAbstractListModel):
    """List model for plugin configuration options"""
    
=======
from PyQt4.QtCore import QVariant, QAbstractListModel, Qt
from PyQt4.Qt import QPixmap, QIcon
import os

class PluginConfigurationListModel(QAbstractListModel):
>>>>>>> gs-ai-patch-1
    def __init__(self, plugins, parent=None):
        super(PluginConfigurationListModel, self).__init__(parent)
        self.plugins = []
        self.pluginList = plugins
    
    def checkPluginConfiguration(self):
<<<<<<< HEAD
        """Validates all plugins and updates their configuration status"""
        self.plugins = []
        for plugin in self.pluginList:
            try:
                config_status = plugin.plugin_object.isConfigured()
                self.plugins.append((plugin, config_status[0]))
            except Exception as e:
                logger.error(f"Error checking configuration for plugin {plugin.name}: {str(e)}")
                self.plugins.append((plugin, False))
        
        # Emit signal that data has changed
        self.layoutChanged.emit()
        
    def rowCount(self, index):
        return len(self.plugins)
    
    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.plugins):
            return None
            
        pluginListItem = self.plugins[index.row()]
        
        try:
            if role == Qt.DisplayRole:
                return pluginListItem[0].name
                
            elif role == Qt.DecorationRole:
                plugin_name = pluginListItem[0].plugin_object.name
                picturePath = os.path.join(os.getcwd(), 'plugins', plugin_name, 'logo.png')
                if os.path.exists(picturePath):
=======
        for plugin in self.pluginList:
            self.plugins.append((plugin,True))
            '''
            if plugin.plugin_object.isConfigured()[0]:
                self.plugins.append((plugin,True))
            else:
                self.plugins.append((plugin,False))
            '''
        
    def rowCount(self,index):
        return len(self.plugins)
    
    def data(self,index,role):
        pluginListItem= self.plugins[index.row()]
        if index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(pluginListItem[0].name)
            if role == Qt.DecorationRole:
                picturePath = os.path.join(os.getcwd(), 'plugins', pluginListItem[0].plugin_object.name, 'logo.png')
                if picturePath and os.path.exists(picturePath):
>>>>>>> gs-ai-patch-1
                    pixmap = QPixmap(picturePath)
                    return QIcon(pixmap)
                else:
                    pixmap = QPixmap(':/creepy/folder')
                    return QIcon(pixmap)
<<<<<<< HEAD
                    
            elif role == Qt.ToolTipRole:
                # Add plugin description as tooltip
                plugin = pluginListItem[0]
                status = "Configured" if pluginListItem[1] else "Not configured"
                description = getattr(plugin, 'description', 'No description available')
                return f"{plugin.name} - {status}\n{description}"
                
            elif role == Qt.BackgroundRole:
                # Highlight plugins with configuration issues
                if not pluginListItem[1]:  # Not configured
                    return QBrush(QColor(255, 220, 220))  # Light red for unconfigured plugins
        
        except Exception as e:
            logger.error(f"Error retrieving plugin data: {str(e)}")
                
        return None
    
    def getPluginAt(self, index):
        """Get plugin at specified index"""
        if 0 <= index < len(self.plugins):
            return self.plugins[index][0]
        return None
=======
        return QVariant()
>>>>>>> gs-ai-patch-1
