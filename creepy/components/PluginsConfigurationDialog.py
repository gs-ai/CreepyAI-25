#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QScrollArea, QCheckBox
from yapsy.PluginManager import PluginManagerSingleton
from models.InputPlugin import InputPlugin
from ui.PluginsConfig import Ui_PluginsConfigurationDialog
from components.PluginConfigurationCheckDialog import PluginConfigurationCheckdialog

class PluginsConfigurationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.PluginManager = PluginManagerSingleton.get()
        self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
        self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
        try:
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error loading plugins: {e}")
        self.ui = Ui_PluginsConfigurationDialog()
        try:
            self.ui.setupUi(self)
        except Exception as e:
            print(f"Error setting up UI: {e}")
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def checkPluginConfiguration(self, plugin):
        self.saveConfiguration()
        checkPluginConfigurationResultDialog = PluginConfigurationCheckdialog()
        isConfigured = plugin.plugin_object.isConfigured()
        if isConfigured[0]:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name + self.trUtf8(' is correctly configured.') + isConfigured[1])
        else:
            checkPluginConfigurationResultDialog.ui.checkPluginConfigurationResultLabel.setText(plugin.name + self.trUtf8(' is not correctly configured.') + isConfigured[1])
        checkPluginConfigurationResultDialog.exec_()
    
    def saveConfiguration(self):
        pages = (self.ui.ConfigurationDetails.widget(i) for i in range(self.ui.ConfigurationDetails.count()))
        for page in pages:
            for widg in [scrollarea.children() for scrollarea in page.children() if type(scrollarea) == QScrollArea]:
                for i in widg[0].children():
                    config_options = {}
                    plugin_name = i.objectName().replace('vboxwidget_container_', '')
                    string_options = {}
                    for j in i.findChildren(QLabel):
                        string_options[str(j.objectName().replace('string_label_', ''))] = str(i.findChild(QLineEdit, j.objectName().replace('label', 'value')).text())
                    boolean_options = {}
                    for k in i.findChildren(QCheckBox):
                        boolean_options[str(k.objectName().replace('boolean_label_', ''))] = str(k.isChecked())
                    config_options['string_options'] = string_options
                    config_options['boolean_options'] = boolean_options
                    plugin = self.PluginManager.getPluginByName(plugin_name, 'Input')
                    if plugin:
                        plugin.plugin_object.saveConfiguration(config_options)
