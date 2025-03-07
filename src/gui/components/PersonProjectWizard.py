#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QTextEdit, QPushButton, QTableView, QGroupBox, QFormLayout, 
                           QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QAbstractTableModel
from models.InputPlugin import InputPlugin
from yapsy.PluginManager import PluginManagerSingleton

logger = logging.getLogger(__name__)

class Ui_PersonProjectWizard(object):
    """UI for the Person Project Wizard dialog"""
    
    def setupUi(self, dialog):
        """Setup the UI elements"""
        dialog.setObjectName("PersonProjectWizard")
        dialog.resize(600, 500)
        dialog.setWindowTitle("New Person Project")
        
        # Main layout
        self.mainLayout = QVBoxLayout(dialog)
        
        # Project details group
        self.projectDetailsGroup = QGroupBox("Project Details", dialog)
        self.projectDetailsLayout = QFormLayout(self.projectDetailsGroup)
        
        self.personProjectNameLabel = QLabel("Project Name:", self.projectDetailsGroup)
        self.personProjectNameValue = QLineEdit(self.projectDetailsGroup)
        self.projectDetailsLayout.addRow(self.personProjectNameLabel, self.personProjectNameValue)
        
        self.personProjectKeywordsLabel = QLabel("Keywords:", self.projectDetailsGroup)
        self.personProjectKeywordsValue = QLineEdit(self.projectDetailsGroup)
        self.projectDetailsLayout.addRow(self.personProjectKeywordsLabel, self.personProjectKeywordsValue)
        
        self.personProjectDescriptionLabel = QLabel("Description:", self.projectDetailsGroup)
        self.personProjectDescriptionValue = QTextEdit(self.projectDetailsGroup)
        self.personProjectDescriptionValue.setMaximumHeight(80)
        self.projectDetailsLayout.addRow(self.personProjectDescriptionLabel, self.personProjectDescriptionValue)
        
        self.mainLayout.addWidget(self.projectDetailsGroup)
        
        # Available plugins group
        self.pluginsGroup = QGroupBox("Available Plugins", dialog)
        self.pluginsLayout = QVBoxLayout(self.pluginsGroup)
        
        self.personProjectAvailablePluginsListView = QTableView(self.pluginsGroup)
        self.pluginsLayout.addWidget(self.personProjectAvailablePluginsListView)
        
        self.personProjectSearchButton = QPushButton("Search for Targets", self.pluginsGroup)
        self.pluginsLayout.addWidget(self.personProjectSearchButton)
        
        self.mainLayout.addWidget(self.pluginsGroup)
        
        # Selected targets group
        self.targetsGroup = QGroupBox("Selected Targets", dialog)
        self.targetsLayout = QVBoxLayout(self.targetsGroup)
        
        self.selectedTargetsTable = QTableWidget(0, 3, self.targetsGroup)
        self.selectedTargetsTable.setHorizontalHeaderLabels(["Plugin", "Name", "ID"])
        self.selectedTargetsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.targetsLayout.addWidget(self.selectedTargetsTable)
        
        self.mainLayout.addWidget(self.targetsGroup)
        
        # Buttons
        self.buttonBox = QHBoxLayout()
        self.cancelButton = QPushButton("Cancel", dialog)
        self.okButton = QPushButton("Create Project", dialog)
        self.okButton.setDefault(True)
        
        self.buttonBox.addStretch()
        self.buttonBox.addWidget(self.cancelButton)
        self.buttonBox.addWidget(self.okButton)
        
        self.mainLayout.addLayout(self.buttonBox)

class PersonProjectWizard(QDialog):
    """Dialog for creating a new person project"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create and setup UI
        self.ui = Ui_PersonProjectWizard()
        self.ui.setupUi(self)
        
        # Initialize selected targets list
        self.selectedTargets = []
        
        # Connect signals to slots
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.okButton.clicked.connect(self.accept)
        self.ui.personProjectSearchButton.clicked.connect(self.searchForTargets)
        
        # Additional setup
        self.setupPluginList()
    
    def setupPluginList(self):
        """Set up the available plugins list"""
        self.plugins = self.loadConfiguredPlugins()
        if not self.plugins:
            QMessageBox.warning(self, "No Plugins", "No plugins are available for creating projects.")
        else:
            # Create a table model for plugins
            from models.ProjectWizardPluginListModel import ProjectWizardPluginListModel
            self.ProjectWizardPluginListModel = ProjectWizardPluginListModel(self.plugins, self)
            self.ui.personProjectAvailablePluginsListView.setModel(self.ProjectWizardPluginListModel)
            
            # Set column widths
            self.ui.personProjectAvailablePluginsListView.setColumnWidth(0, 150)
            self.ui.personProjectAvailablePluginsListView.setColumnWidth(1, 280)
            self.ui.personProjectAvailablePluginsListView.setColumnWidth(2, 120)
            
            logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def loadConfiguredPlugins(self):
        """
        Load available plugins from the plugin manager
        """
        try:
            logger.debug("Loading plugins for PersonProjectWizard")
            plugins = []
            
            # Try to get plugins from yapsy manager
            pluginManager = PluginManagerSingleton.get()
            pluginManager.setCategoriesFilter({'Input': InputPlugin})
            pluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
            pluginManager.locatePlugins()
            pluginManager.loadPlugins()
            
            for plugin in pluginManager.getAllPlugins():
                if hasattr(plugin.plugin_object, 'returnLocations'):
                    plugins.append(plugin)
                    logger.debug(f"Found plugin: {plugin.name}")
            
            return plugins
        except Exception as e:
            logger.error(f"Error loading plugins: {str(e)}")
            QMessageBox.critical(self, "Plugin Error", f"Error loading plugins: {str(e)}")
            return []
    
    def searchForTargets(self):
        """
        Search for targets using the selected plugins
        """
        try:
            # Get project search terms
            project_name = self.ui.personProjectNameValue.text()
            keywords = self.ui.personProjectKeywordsValue.text()
            
            if not project_name and not keywords:
                QMessageBox.warning(self, "Missing Information", 
                                  "Please enter a project name or keywords to search for.")
                return
            
            # Determine which plugins are selected
            selected_plugins = []
            for plugin in self.plugins:
                if getattr(plugin, 'selected', False):
                    selected_plugins.append(plugin)
            
            if not selected_plugins:
                QMessageBox.warning(self, "No Plugins Selected", 
                                  "Please select at least one plugin to search with.")
                return
                
            logger.debug(f"Search initiated with {len(selected_plugins)} plugins")
            
            # Primary search term is project name or first keyword
            search_term = project_name
            if not search_term and keywords:
                search_term = keywords.split(',')[0].strip()
            
            logger.info(f"Searching with term: {search_term}")
            QMessageBox.information(self, "Search", f"Searching for '{search_term}'...")
            
            found_targets = []
            
            # Try to execute actual plugin search if plugins are available
            for plugin in selected_plugins:
                try:
                    logger.info(f"Searching with plugin: {plugin.name}")
                    plugin_targets = plugin.plugin_object.searchForTargets(search_term)
                    if plugin_targets:
                        logger.info(f"Plugin {plugin.name} returned {len(plugin_targets)} targets")
                        # Ensure each target has a plugin name to track the source
                        for target in plugin_targets:
                            if 'pluginName' not in target:
                                target['pluginName'] = plugin.name
                        found_targets.extend(plugin_targets)
                    else:
                        logger.info(f"Plugin {plugin.name} returned no targets")
                except Exception as e:
                    logger.error(f"Error using plugin {plugin.name}: {str(e)}")
                    QMessageBox.warning(self, "Plugin Error", 
                                      f"Error using plugin {plugin.name}: {str(e)}")
            
            # If no real targets found, use a dummy target
            if not found_targets:
                # Only use dummy target in development/debug mode
                if logger.level <= logging.DEBUG:
                    logger.info("No targets found from plugins, using dummy target")
                    dummy_target = {
                        'pluginName': 'DummyPlugin',
                        'targetName': f'Example Target for {search_term}',
                        'targetUser': f'user_{search_term.replace(" ", "_").lower()}',
                        'targetId': f'dummy_{search_term.replace(" ", "_").lower()}'
                    }
                    found_targets.append(dummy_target)
                    QMessageBox.information(self, "Development Mode", "Using dummy target since no real targets were found.")
                else:
                    QMessageBox.information(self, "No Results", 
                                          f"No targets found for '{search_term}'. Try different search terms or plugins.")
                    return
            
            # Add all found targets to our selection
            self.selectedTargets.extend(found_targets)
            QMessageBox.information(self, "Search Complete", 
                                  f"Found {len(found_targets)} targets for '{search_term}'")
            
            logger.info(f"Selected targets updated, now have {len(self.selectedTargets)} targets")
            self.updateTargetsTable()
            
        except Exception as e:
            logger.error(f"Error searching for targets: {str(e)}")
            QMessageBox.critical(self, "Search Error", f"Error searching for targets: {str(e)}")
    
    def updateTargetsTable(self):
        """Update the selected targets table with current targets"""
        # Clear the table
        self.ui.selectedTargetsTable.setRowCount(0)
        
        # Add rows for each target
        for i, target in enumerate(self.selectedTargets):
            self.ui.selectedTargetsTable.insertRow(i)
            self.ui.selectedTargetsTable.setItem(i, 0, QTableWidgetItem(target.get('pluginName', '')))
            self.ui.selectedTargetsTable.setItem(i, 1, QTableWidgetItem(target.get('targetName', '')))
            self.ui.selectedTargetsTable.setItem(i, 2, QTableWidgetItem(target.get('targetId', '')))
    
    def readSearchConfiguration(self):
        """
        Read search configuration from UI controls and selected plugins
        
        Returns:
            List of dictionaries with pluginName and searchOptions
        """
        config = []
        for plugin in self.plugins:
            if getattr(plugin, 'selected', False):
                # Get plugin-specific search options
                # This could be expanded to include plugin-specific UI for search options
                config.append({
                    'pluginName': plugin.name,
                    'searchOptions': {}  # Default empty for now
                })
        return config