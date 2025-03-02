#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QDialog, QMessageBox, QCheckBox, QLineEdit
from PyQt5.QtCore import Qt
from ui.PluginsConfigurationDialogUI import Ui_PluginsConfigurationDialog
from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin

class PluginsConfigurationDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        
    def checkPluginConfiguration(self, plugin):
        """
        Checks if a plugin is properly configured
        """
        isConfigured = plugin.plugin_object.isConfigured()
        if isConfigured[0]:
            QMessageBox.information(self, self.tr("Plugin Configuration Check"), 
                                   self.tr("Plugin is properly configured."))
        else:
            QMessageBox.warning(self, self.tr("Plugin Configuration Check"), 
                               self.tr("Plugin is not properly configured.\n") + isConfigured[1])
    
    def saveConfiguration(self):
        """
        Saves all plugins' configurations
        """
        try:
            # Iterate over all pages in the stacked widget
            for i in range(self.ui.ConfigurationDetails.count()):
                page = self.ui.ConfigurationDetails.widget(i)
                pluginName = page.objectName().replace("page_", "")
                
                # Find the plugin object
                plugin = None
                for pl in self.PluginManager.getAllPlugins():
                    if pl.name == pluginName:
                        plugin = pl
                        break
                
                if not plugin:
                    continue
                
                # Collect the values from string and boolean options
                config = {'string_options': {}, 'boolean_options': {}}
                
                # Process string options (QLineEdit widgets)
                for child in page.findChildren(QLineEdit):
                    if child.objectName().startswith("string_value_"):
                        key = child.objectName().replace("string_value_", "")
                        config['string_options'][key] = child.text()
                
                # Process boolean options (QCheckBox widgets)
                for child in page.findChildren(QCheckBox):
                    if child.objectName().startswith("boolean_label_"):
                        key = child.objectName().replace("boolean_label_", "")
                        config['boolean_options'][key] = str(child.isChecked())
                
                # Save the configuration
                plugin.plugin_object.saveConfiguration(config)
                
            QMessageBox.information(self, self.tr("Configuration Saved"), 
                                   self.tr("All plugin configurations have been saved."))
            
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), 
                               self.tr(f"An error occurred while saving the configuration: {str(e)}"))
