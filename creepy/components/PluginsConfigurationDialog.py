#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging
from PyQt5.QtWidgets import (QDialog, QMessageBox, QCheckBox, QLineEdit,
                           QLabel, QPushButton, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from ui.PluginsConfigurationDialogUI import Ui_PluginsConfigurationDialog
from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin
from components.PluginErrorsDialog import PluginErrorsDialog

# Set up logging
logger = logging.getLogger(__name__)

class PluginsConfigurationDialog(QDialog):
    """Dialog for configuring CreepyAI plugins"""
    
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        self.modified_plugins = set()
        
        # Initialize the plugin manager
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
        self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
        self.PluginManager.locatePlugins()
        self.PluginManager.loadPlugins()
        
        # Connect signals and slots
        self.ui.ButtonSave.clicked.connect(self.saveConfiguration)
        self.ui.ButtonClose.clicked.connect(self.close)
        
        # Add error report button
        self.ui.ButtonErrors = QPushButton(QIcon(":/creepy/warning"), "Error Report")
        self.ui.ButtonErrors.clicked.connect(self.showErrorReport)
        self.ui.buttonLayout.insertWidget(1, self.ui.ButtonErrors)
        
        # Connect the plugin list selection change
        self.ui.PluginsList.selectionModel().selectionChanged.connect(self.onPluginSelectionChanged)
        
        # Setup change tracking
        for i in range(self.ui.ConfigurationDetails.count()):
            page = self.ui.ConfigurationDetails.widget(i)
            for child in page.findChildren(QLineEdit):
                child.textChanged.connect(lambda: self.markModified())
            for child in page.findChildren(QCheckBox):
                child.stateChanged.connect(lambda: self.markModified())
        
    def markModified(self):
        """Mark the current plugin as modified"""
        current_index = self.ui.PluginsList.currentIndex().row()
        if current_index >= 0:
            plugin = self.ui.PluginsList.model().getPluginAt(current_index)
            if plugin:
                self.modified_plugins.add(plugin.name)
                
                # Update save button status
                self.ui.ButtonSave.setEnabled(True)
                self.ui.ButtonSave.setText(f"Save ({len(self.modified_plugins)})")
    
    def onPluginSelectionChanged(self, selected, deselected):
        """Handle plugin selection change in the list view"""
        indices = selected.indexes()
        if indices:
            plugin_index = indices[0].row()
            plugin = self.ui.PluginsList.model().getPluginAt(plugin_index)
            if plugin:
                # Show status information for the selected plugin
                status_widget = QWidget()
                status_layout = QVBoxLayout(status_widget)
                
                # Show configuration status
                config_status = plugin.plugin_object.isConfigured()
                status_text = f"Status: {'Configured' if config_status[0] else 'Not configured'}"
                if not config_status[0]:
                    status_text += f" - {config_status[1]}"
                
                status_label = QLabel(status_text)
                if config_status[0]:
                    status_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    status_label.setStyleSheet("color: red; font-weight: bold;")
                    
                status_layout.addWidget(status_label)
                
                # Show error count
                error_count = getattr(plugin.plugin_object, 'error_count', 0)
                if error_count > 0:
                    error_label = QLabel(f"Errors: {error_count}")
                    error_label.setStyleSheet("color: red;")
                    status_layout.addWidget(error_label)
                
                # Add status widget to page
                page_index = self.ui.ConfigurationDetails.currentIndex()
                page = self.ui.ConfigurationDetails.widget(page_index)
                
                # Clear previous status widget if exists
                for child in page.children():
                    if isinstance(child, QWidget) and child.objectName() == "plugin_status_widget":
                        child.setParent(None)
                
                status_widget.setObjectName("plugin_status_widget")
                status_widget.setParent(page)
                status_widget.move(10, 10)
                status_widget.show()
        
    def checkPluginConfiguration(self, plugin):
        """
        Checks if a plugin is properly configured
        
        Args:
            plugin: Plugin object to check
        """
        try:
            isConfigured = plugin.plugin_object.isConfigured()
            if isConfigured[0]:
                QMessageBox.information(self, self.tr("Plugin Configuration Check"), 
                                     self.tr("Plugin is properly configured."))
            else:
                QMessageBox.warning(self, self.tr("Plugin Configuration Check"), 
                                 self.tr("Plugin is not properly configured.\n") + isConfigured[1])
        except Exception as e:
            logger.error(f"Error checking plugin configuration: {str(e)}")
            QMessageBox.critical(self, self.tr("Error"), 
                              self.tr(f"An error occurred while checking the plugin: {str(e)}"))
    
    def saveConfiguration(self):
        """Saves all plugins' configurations"""
        success_count = 0
        error_count = 0
        error_messages = []
        
        try:
            # Iterate over all pages in the stacked widget
            for i in range(self.ui.ConfigurationDetails.count()):
                page = self.ui.ConfigurationDetails.widget(i)
                pluginName = page.objectName().replace("page_", "")
                
                # Only save modified plugins
                if pluginName not in self.modified_plugins:
                    continue
                
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
                
                try:
                    # Save the configuration
                    plugin.plugin_object.saveConfiguration(config)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"{plugin.name}: {str(e)}")
                    logger.error(f"Error saving configuration for {plugin.name}: {str(e)}")
            
            # Update modified plugins set
            self.modified_plugins.clear()
            self.ui.ButtonSave.setText("Save")
            self.ui.ButtonSave.setEnabled(False)
            
            # Show results
            if error_count == 0:
                QMessageBox.information(self, self.tr("Configuration Saved"), 
                                     self.tr(f"All {success_count} plugin configurations have been saved."))
            else:
                error_text = "\n".join(error_messages)
                QMessageBox.warning(self, self.tr("Configuration Partially Saved"), 
                                  self.tr(f"Saved {success_count} configurations with {error_count} errors:\n{error_text}"))
            
        except Exception as e:
            logger.error(f"Error in saveConfiguration: {str(e)}")
            QMessageBox.critical(self, self.tr("Error"), 
                              self.tr(f"An error occurred while saving the configuration: {str(e)}"))
    
    def showErrorReport(self):
        """Show the plugin errors dialog"""
        dialog = PluginErrorsDialog(self)
        dialog.exec_()
