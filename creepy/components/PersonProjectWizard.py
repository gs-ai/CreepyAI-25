#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QWizard, QMessageBox, QWidget, QScrollArea, QLineEdit, QLabel, QVBoxLayout, QCheckBox, QGridLayout
from PyQt5.QtCore import QString
from models.PluginConfigurationListModel import PluginConfigurationListModel
from models.ProjectWizardPossibleTargetsTable import ProjectWizardPossibleTargetsTable
from models.InputPlugin import InputPlugin
from yapsy.PluginManager import PluginManagerSingleton
from ui.PersonProjectWizard import Ui_personProjectWizard

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class PersonProjectWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_personProjectWizard()
        self.ui.setupUi(self)
        self.selectedTargets = []
        self.enabledPlugins = []
        self.page(0).registerField('name*', self.ui.personProjectNameValue)
        self.ui.btnAddTarget.clicked.connect(self.addTargetsToSelected)
        self.ui.btnRemoveTarget.clicked.connect(self.removeTargetsFromSelected)
        self.ui.personProjectSearchForValue.returnPressed.connect(self.ui.personProjectSearchButton.setFocus)
        
    def addTargetsToSelected(self):
        try:
            selected = self.ui.personProjectSearchResultsTable.selectionModel().selectedRows()
            newTargets = [self.ui.personProjectSearchResultsTable.model().targets[i.row()] for i in selected]
            self.ui.personProjectSelectedTargetsTable.model().insertRows(newTargets, len(newTargets))
        except Exception as e:
            self.showWarning('Error', f'Failed to add targets: {str(e)}')

    def removeTargetsFromSelected(self):
        try:
            selected = self.ui.personProjectSelectedTargetsTable.selectionModel().selectedRows()
            toRemove = [self.ui.personProjectSelectedTargetsTable.model().targets[i.row()] for i in selected]
            self.ui.personProjectSelectedTargetsTable.model().removeRows(toRemove, len(toRemove))
        except Exception as e:
            self.showWarning('Error', f'Failed to remove targets: {str(e)}')
        
    def showWarning(self, title, text):
        QMessageBox.warning(self, title, text)
        
    def initializePage(self, i):
        if i == 2:
            self.checkIfSelectedTargets()
            self.storeSelectedTargets()
            self.showPluginsSearchOptions()
            
    def checkIfSelectedTargets(self):
        if not self.ProjectWizardSelectedTargetsTable.targets:
            self.showWarning('No target selected', 'Please drag and drop your targets to the selected targets before proceeding')
            self.back()
            self.next()
    
    def storeSelectedTargets(self):
        self.selectedTargets = []
        for target in self.ProjectWizardSelectedTargetsTable.targets:
            self.selectedTargets.append({'pluginName': target['pluginName'],
                                         'targetUsername': target['targetUsername'],
                                         'targetUserid': target['targetUserid'],
                                         'targetFullname': target['targetFullname']})

    def searchForTargets(self):
        search_term = self.ui.personProjectSearchForValue.text().strip()
        if not search_term:
            self.showWarning('Empty Search Term', 'Please enter a search term')
            return
        try:
            selectedPlugins = list(self.ProjectWizardPluginListModel.checkedPlugins)
            possibleTargets = []
            for pluginName in selectedPlugins:
                plugin = self.PluginManager.getPluginByName(pluginName, 'Input')
                pluginTargets = plugin.plugin_object.searchForTargets(search_term)
                if pluginTargets:
                    possibleTargets.extend(pluginTargets)
            self.ProjectWizardPossibleTargetsTable = ProjectWizardPossibleTargetsTable(possibleTargets, self)
            self.ui.personProjectSearchResultsTable.setModel(self.ProjectWizardPossibleTargetsTable)
            self.ui.personProjectSelectedTargetsTable.setModel(self.ProjectWizardSelectedTargetsTable)
        except Exception as e:
            self.showWarning('Error', f'Failed to search for targets: {str(e)}')
    
    def loadConfiguredPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
            self.PluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            try:
                self.PluginManager.locatePlugins()
                self.PluginManager.loadPlugins()
            except Exception as e:
                self.showWarning('Error', f'Failed to load plugins: {str(e)}')
            pluginList = sorted(self.PluginManager.getAllPlugins(), key=lambda x: x.name)
            return [[plugin, 0] for plugin in pluginList]
        except Exception as e:
            self.showWarning('Error', f'Failed to load plugins: {str(e)}')
            return []
    
    def getNameForConfigurationOption(self, key):
        pass
            
    def showPluginsSearchOptions(self):
        try:
            pl = []
            for pluginName in set(target['pluginName'] for target in self.ProjectWizardSelectedTargetsTable.targets):
                plugin = self.PluginManager.getPluginByName(pluginName, 'Input')
                self.enabledPlugins.append(plugin)
                pl.append(plugin)
                page = QWidget()
                page.setObjectName(f'searchconfig_page_{plugin.name}')
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                layout = QVBoxLayout()
                titleLabel = QLabel(f'{plugin.name} Search Options')
                layout.addWidget(titleLabel)
                vboxWidget = QWidget()
                vboxWidget.setObjectName(f'searchconfig_vboxwidget_container_{plugin.name}')
                vbox = QGridLayout()
                vbox.setObjectName(f'searchconfig_vbox_container_{plugin.name}')
                gridLayoutRowIndex = 0
                pluginStringOptions = plugin.plugin_object.readConfiguration('search_string_options')[1]
                if pluginStringOptions:
                    for idx, item in enumerate(pluginStringOptions.keys()):
                        itemLabel = plugin.plugin_object.getLabelForKey(item)
                        label = QLabel()
                        label.setObjectName(f'searchconfig_string_label_{item}')
                        label.setText(itemLabel)
                        vbox.addWidget(label, idx, 0)
                        value = QLineEdit()
                        value.setObjectName(f'searchconfig_string_value_{item}')
                        value.setText(pluginStringOptions[item])
                        vbox.addWidget(value, idx, 1)
                        gridLayoutRowIndex = idx + 1
                pluginBooleanOptions = plugin.plugin_object.readConfiguration('search_boolean_options')[1]
                if pluginBooleanOptions:
                    for idx, item in enumerate(pluginBooleanOptions.keys()):
                        itemLabel = plugin.plugin_object.getLabelForKey(item)
                        cb = QCheckBox(itemLabel)
                        cb.setObjectName(f'searchconfig_boolean_label_{item}')
                        if pluginBooleanOptions[item] == 'True':
                            cb.toggle()
                        vbox.addWidget(cb, gridLayoutRowIndex + idx, 0)
                if not pluginBooleanOptions and not pluginStringOptions:
                    label = QLabel()
                    label.setObjectName('no_search_config_options')
                    label.setText('This plugin does not offer any search options.')
                    vbox.addWidget(label, 0, 0)
                vboxWidget.setLayout(vbox)
                scroll.setWidget(vboxWidget)
                layout.addWidget(scroll)
                layout.addStretch(1)
                page.setLayout(layout)
                self.ui.searchConfiguration.addWidget(page)
            self.ui.searchConfiguration.setCurrentIndex(0)
            self.SearchConfigPluginConfigurationListModel = PluginConfigurationListModel(pl, self)
            self.SearchConfigPluginConfigurationListModel.checkPluginConfiguration()
            self.ui.personProjectWizardSearchConfigPluginsList.setModel(self.SearchConfigPluginConfigurationListModel)
            self.ui.personProjectWizardSearchConfigPluginsList.clicked.connect(self.changePluginConfigurationPage)
        except Exception as e:
            self.showWarning('Error', f'Failed to show plugin search options: {str(e)}')

    def changePluginConfigurationPage(self, modelIndex):
        self.ui.searchConfiguration.setCurrentIndex(modelIndex.row())
        
    def readSearchConfiguration(self):
        enabledPlugins = []
        try:
            pages = (self.ui.searchConfiguration.widget(i) for i in range(self.ui.searchConfiguration.count()))
            for page in pages:
                for widg in [scrollarea.children() for scrollarea in page.children() if type(scrollarea) == QScrollArea]:
                    for i in widg[0].children():
                        plugin_name = str(i.objectName().replace('searchconfig_vboxwidget_container_', ''))
                        string_options = {}
                        for j in i.findChildren(QLabel):
                            if str(j.text()).startswith('searchconfig'):
                                string_options[str(j.objectName().replace('searchconfig_string_label_', ''))] = str(i.findChild(QLineEdit, j.objectName().replace('label', 'value')).text())
                        boolean_options = {}
                        for k in i.findChildren(QCheckBox):
                            boolean_options[str(k.objectName().replace('searchconfig_boolean_label_', ''))] = str(k.isChecked())
                enabledPlugins.append({'pluginName': plugin_name, 'searchOptions': {'string': string_options, 'boolean': boolean_options}})
        except Exception as e:
            self.showWarning('Error', f'Failed to read search configuration: {str(e)}')
        return enabledPlugins
