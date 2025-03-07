#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt5.QtGui import QIcon, QPixmap

logger = logging.getLogger(__name__)

class PluginConfigurationListModel(QAbstractListModel):
    """List model for displaying plugins in configuration dialog"""
    
    def __init__(self, plugins, parent=None):
        super(PluginConfigurationListModel, self).__init__(parent)
        self.plugins = plugins
        # Dictionary to store configuration status of plugins
        self.pluginStatus = {}
        
        # Icons for configuration status
        self.configuredIcon = QIcon(':/creepy/tick')
        self.notConfiguredIcon = QIcon(':/creepy/exclamation')
        
        # Check configuration status of all plugins
        self.checkPluginConfiguration()
    
    def rowCount(self, parent=QModelIndex()):
        """Return the number of plugins in the model"""
        return len(self.plugins)
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given index and role"""
        if not index.isValid() or not (0 <= index.row() < len(self.plugins)):
            return None
            
        plugin = self.plugins[index.row()]
        
        if role == Qt.DisplayRole:
            return plugin.name
            
        elif role == Qt.DecorationRole:
            # Return the status icon
            if plugin.name in self.pluginStatus and self.pluginStatus[plugin.name]:
                return self.configuredIcon
            else:
                return self.notConfiguredIcon
                
        elif role == Qt.ToolTipRole:
            # Provide a tooltip showing configuration status
            if plugin.name in self.pluginStatus and self.pluginStatus[plugin.name]:
                return "Plugin is correctly configured"
            else:
                return "Plugin configuration is missing or invalid"
                
        return None
    
    def checkPluginConfiguration(self):
        """
        Check if all plugins are properly configured
        Updates the configuration status dictionary
        """
        try:
            for plugin in self.plugins:
                try:
                    # Call isConfigured method on plugin 
                    result, message = plugin.plugin_object.isConfigured()
                    self.pluginStatus[plugin.name] = result
                    logger.debug(f"Plugin {plugin.name} configuration status: {result}")
                except Exception as e:
                    logger.error(f"Error checking configuration for plugin {plugin.name}: {str(e)}")
                    self.pluginStatus[plugin.name] = False
                    
            # Notify that the model has changed to update the view
            self.layoutChanged.emit()
        except Exception as e:
            logger.error(f"Error checking plugin configurations: {str(e)}")
    
    def getConfiguredStatus(self, plugin_name):
        """Get configuration status for a specific plugin"""
        if plugin_name in self.pluginStatus:
            return self.pluginStatus[plugin_name]
        return False
