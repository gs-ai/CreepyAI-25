# Note: This file was moved from components/PluginsConfigurationDialog.py to ui/

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging
from PyQt5.QtWidgets import (QDialog, QMessageBox, QCheckBox, QLineEdit,
                           QLabel, QPushButton, QVBoxLayout, QWidget, QTableView, QStackedWidget, QHBoxLayout, QListView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# Fix the imports - try multiple possible UI files
try:
    from ui.PluginsConfigurationDialogUI import Ui_PluginsConfigurationDialog
except ModuleNotFoundError:
    try:
        from ui.PluginsConfig import Ui_PluginsConfigurationDialog
    except ModuleNotFoundError:
        from ui.PluginsConfigurationDialogUI import Ui_PluginsConfigurationDialog

from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin
from ui.PluginErrorsDialog import PluginErrorsDialog

# Set up logging
logger = logging.getLogger(__name__)

class Ui_PluginsConfigurationDialog(object):
    """UI for the Plugins Configuration dialog"""
    
    def setupUi(self, dialog):
        # Set basic properties
        dialog.setObjectName("PluginsConfigurationDialog")
        dialog.resize(800, 600)
        dialog.setWindowTitle("Plugins Configuration")
        
        # Main layout
        self.mainLayout = QHBoxLayout(dialog)
        
        # Left side - plugins list
        self.leftPanel = QVBoxLayout()
        self.pluginsListLabel = QLabel("Available Plugins:", dialog)
        self.leftPanel.addWidget(self.pluginsListLabel)
        
        self.PluginsList = QListView(dialog)
        self.PluginsList.setObjectName("PluginsList")
        self.leftPanel.addWidget(self.PluginsList)
        
        self.mainLayout.addLayout(self.leftPanel, 1)
        
        # Right side - plugin configuration
        self.ConfigurationDetails = QStackedWidget(dialog)
        self.ConfigurationDetails.setObjectName("ConfigurationDetails")
        self.mainLayout.addWidget(self.ConfigurationDetails, 3)

class PluginsConfigurationDialog(QDialog):
    """Dialog for configuring plugins"""
    
    def __init__(self, parent=None):
        super(PluginsConfigurationDialog, self).__init__(parent)
        
        # Setup UI
        self.ui = Ui_PluginsConfigurationDialog()
        self.ui.setupUi(self)
        
        # Center the dialog
        self.center_on_screen()
        
        # Initialize plugin manager
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
            self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            logger.error(f"Error initializing plugin manager: {str(e)}")
            QMessageBox.critical(self, "Plugin Manager Error", 
                               f"Failed to initialize plugin manager: {str(e)}")
    
    def center_on_screen(self):
        """Center the dialog on screen"""
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QRect
        
        app_rect = QApplication.desktop().availableGeometry()
        form_rect = self.frameGeometry()
        
        form_rect.moveCenter(app_rect.center())
        self.move(form_rect.topLeft())
    
    def checkPluginConfiguration(self, plugin):
        """Check if a plugin is properly configured"""
        try:
            logger.debug(f"Checking configuration for plugin: {plugin.name}")
            
            # Call isConfigured method on the plugin object
            result, message = plugin.plugin_object.isConfigured()
            
            # Show the result to the user
            if result:
                QMessageBox.information(self, "Configuration Valid", 
                                       f"The plugin {plugin.name} is configured correctly.\n\n{message}")
            else:
                QMessageBox.warning(self, "Configuration Invalid", 
                                   f"The plugin {plugin.name} is not configured correctly.\n\n{message}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error checking plugin configuration: {str(e)}")
            QMessageBox.critical(self, "Configuration Check Error", 
                               f"Error checking configuration for {plugin.name}:\n\n{str(e)}")
            return False
    
    def saveConfiguration(self):
        """Save configuration for all plugins"""
        try:
            success_count = 0
            error_count = 0
            
            # Loop through all pages in the stacked widget
            for i in range(self.ui.ConfigurationDetails.count()):
                page = self.ui.ConfigurationDetails.widget(i)
                plugin = self.PluginManager.getAllPlugins()[i]
                
                logger.debug(f"Saving configuration for plugin: {plugin.name}")
                
                # Collect string options
                string_options = {}
                for child in page.findChildren(QLineEdit):
                    if child.objectName().startswith('string_value_'):
                        option_name = child.objectName()[len('string_value_'):]
                        string_options[option_name] = child.text()
                
                # Collect boolean options
                boolean_options = {}
                for child in page.findChildren(QCheckBox):
                    if child.objectName().startswith('boolean_label_'):
                        option_name = child.objectName()[len('boolean_label_'):]
                        boolean_options[option_name] = str(child.isChecked())
                
                # Save configuration
                try:
                    config = {
                        'string_options': string_options,
                        'boolean_options': boolean_options
                    }
                    
                    result = plugin.plugin_object.saveConfiguration(config)
                    if result:
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(f"Failed to save configuration for {plugin.name}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error saving configuration for {plugin.name}: {str(e)}")
            
            # Show result message
            if error_count == 0:
                QMessageBox.information(self, "Configuration Saved", 
                                      f"Configuration for {success_count} plugins saved successfully.")
            else:
                QMessageBox.warning(self, "Configuration Saved with Errors", 
                                  f"Configuration saved for {success_count} plugins.\n"
                                  f"Failed to save for {error_count} plugins.\n\n"
                                  f"Check the log for details.")
        
        except Exception as e:
            logger.error(f"Error in saveConfiguration: {str(e)}")
            QMessageBox.critical(self, "Configuration Save Error", 
                               f"An error occurred while saving configurations:\n\n{str(e)}")
