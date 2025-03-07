#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

# Ensure the directories are in the Python path - update this to use absolute paths
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.join(project_dir, 'ui'))
sys.path.insert(0, os.path.join(project_dir, 'models'))
sys.path.insert(0, os.path.join(project_dir, 'components'))
sys.path.insert(0, os.path.join(project_dir, 'utilities'))

import datetime
import logging
import shelve
import functools
import csv
import urllib.request
from packaging.version import Version

# Import non-widget related modules first
import platform

# Set up logging with better directory handling
log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'creepy_main.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Capture stderr and stdout to log files
stdout_log = os.path.join(log_dir, 'creepy_stdout.log')
stderr_log = os.path.join(log_dir, 'creepy_stderr.log')
sys.stdout = open(stdout_log, 'w')
sys.stderr = open(stderr_log, 'w')

# Import QtCore first to set attributes before QApplication creation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Set required attributes for Qt WebEngine
from PyQt5.QtCore import QCoreApplication
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Remove the early QApplication creation block:
# from PyQt5.QtWidgets import QApplication
# app = QApplication(sys.argv)

# Now it's safe to import other modules that may create widgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QDateTime, QDate, QRect
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QWidget, QScrollArea, QVBoxLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QStackedWidget, QGridLayout, QMenu, QTableWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from utilities.webengine_compat import WebEnginePageCompat
import resources.creepy_resources_rc

# Import the ResourceLoader
from utilities.ResourceLoader import ResourceLoader

# Add after existing imports
from utilities.gui_compatibility import ButtonFactory, fix_tkinter_buttons_in_pyqt

# Now import the local modules
from CreepyUI import Ui_CreepyMainWindow
from yapsy.PluginManager import PluginManagerSingleton
from models.PluginManager import PluginManager  # New optimized plugin manager
from models.LocationsList import LocationsTableModel
from models.Project import Project
from models.Location import Location
from models.PluginConfigurationListModel import PluginConfigurationListModel
from models.ProjectWizardPluginListModel import ProjectWizardPluginListModel
from models.ProjectWizardSelectedTargetsTable import ProjectWizardSelectedTargetsTable
from models.InputPlugin import InputPlugin
from models.ProjectTree import ProjectNode, LocationsNode, AnalysisNode, ProjectTreeModel, ProjectTreeNode
from components.PersonProjectWizard import PersonProjectWizard
from components.PluginsConfigurationDialog import PluginsConfigurationDialog
from components.FilterLocationsDateDialog import FilterLocationsDateDialog
from components.FilterLocationsPointDialog import FilterLocationsPointDialog
from components.AboutDialog import AboutDialog
from components.VerifyDeleteDialog import VerifyDeleteDialog
from components.update_check_dialog import UpdateCheckDialog
from utilities import GeneralUtilities

# Initialize the resource loader
resource_loader = ResourceLoader.instance()


class MainWindow(QMainWindow):

    class analyzeProjectThread(QThread):
        locations_signal = pyqtSignal(object)

        def __init__(self, project):
            super().__init__()
            self.project = project

        def run(self):
            pluginManager = PluginManagerSingleton.get()
            pluginManager.setCategoriesFilter({'Input': InputPlugin})
            pluginManager.setPluginPlaces([os.path.join(os.getcwd(), 'plugins')])
            pluginManager.locatePlugins()
            pluginManager.loadPlugins()
            locationsList = []
            for target in self.project.selectedTargets:
                pluginObject = pluginManager.getPluginByName(target['pluginName'], 'Input').plugin_object
                runtimeConfig = next((pl['searchOptions'] for pl in self.project.enabledPlugins if pl['pluginName'] == target['pluginName']), None)
                targetLocations = pluginObject.returnLocations(target, runtimeConfig)
                if targetLocations:
                    for loc in targetLocations:
                        location = Location()
                        location.plugin = loc['plugin']
                        location.datetime = loc['date']
                        location.longitude = loc['lon']
                        location.latitude = loc['lat']
                        location.context = loc['context']
                        location.infowindow = loc['infowindow']
                        location.shortName = loc['shortName']
                        location.updateId()
                        location.visible = True
                        locationsList.append(location)
            # remove duplicates if any
            for l in locationsList:
                if l.id not in [loc.id for loc in self.project.locations]:
                    self.project.locations.append(l)
            # sort on date
            self.project.locations.sort(key=lambda x: x.datetime, reverse=True)
            self.locations_signal.emit(self.project)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.version = "1.1"
        self.ui = Ui_CreepyMainWindow()
        self.ui.setupUi(self)
        # Create folders for projects and temp if they do not exist
        os.makedirs(os.path.join(os.getcwd(), 'projects'), exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'temp'), exist_ok=True)
        self.projectsList = []
        self.currentProject = None
        self.ui.webPage = WebEnginePageCompat()
        
        # Ensure the map URL is correct
        map_url = QUrl.fromLocalFile(os.path.join(os.getcwd(), 'include', 'map.html'))
        self.ui.webPage.mainFrame().setUrl(map_url)
        
        self.ui.mapWebView.setPage(self.ui.webPage)
        self.ui.menuView.addAction(self.ui.dockWProjects.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWLocationsList.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWCurrentLocationDetails.toggleViewAction())
        self.ui.actionPluginsConfiguration.triggered.connect(self.showPluginsConfigurationDialog)
        self.ui.actionNewPersonProject.triggered.connect(self.showPersonProjectWizard)
        self.ui.actionAnalyzeCurrentProject.triggered.connect(self.analyzeProject)
        self.ui.actionReanalyzeCurrentProject.triggered.connect(self.analyzeProject)
        self.ui.actionDrawCurrentProject.triggered.connect(self.presentLocations)
        self.ui.actionExportCSV.triggered.connect(self.exportProjectCSV)
        self.ui.actionExportKML.triggered.connect(self.exportProjectKML)
        self.ui.actionExportFilteredCSV.triggered.connect(functools.partial(self.exportProjectCSV, filtering=True))
        self.ui.actionExportFilteredKML.triggered.connect(functools.partial(self.exportProjectKML, filtering=True))
        self.ui.actionDeleteCurrentProject.triggered.connect(self.deleteCurrentProject)
        self.ui.actionFilterLocationsDate.triggered.connect(self.showFilterLocationsDateDialog)
        self.ui.actionFilterLocationsPosition.triggered.connect(self.showFilterLocationsPointDialog)
        self.ui.actionRemoveFilters.triggered.connect(self.removeAllFilters)
        self.ui.actionShowHeatMap.toggled.connect(self.toggleHeatMap)
        self.ui.actionReportProblem.triggered.connect(GeneralUtilities.reportProblem)
        self.ui.actionAbout.triggered.connect(self.showAboutDialog)
        self.ui.actionCheckUpdates.triggered.connect(self.checkForUpdatedVersion)
        self.ui.actionExit.triggered.connect(self.close)
        self.loadProjectsFromStorage()
        # If option enabled check for updated version
        self.loadConfiguredPlugins()
        
        # Center the main window
        self.center_window()

    def center_window(self):
        """Center the main window on screen"""
        from PyQt5.QtWidgets import QApplication
        
        screen_geometry = QApplication.desktop().availableGeometry()
        window_geometry = self.frameGeometry()
        
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        
        self.move(window_geometry.topLeft())

    def loadConfiguredPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setCategoriesFilter({'Input': InputPlugin})
            self.PluginManager.setPluginPlaces([
                os.path.join(os.getcwd(), 'plugins'),
                '/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'
            ])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            self.showWarning('Error', f'Failed to load plugins: {str(e)}')

    def checkForUpdatedVersion(self):
        '''
        Checks www.geocreepy.com for an updated version and returns a tuple with the
        result and the latest version number
        '''
        try:
            latestVersion = urllib.request.urlopen("http://www.geocreepy.com/version.html").read().decode('utf-8').rstrip()
            updateCheckDialog = UpdateCheckDialog()
            updateCheckDialog.ui.versionsTableWidget.setHorizontalHeaderLabels(('', 'Component', 'Status', 'Installed', 'Available'))
            updateCheckDialog.ui.versionsTableWidget.setItem(0, 1, QTableWidgetItem('Creepy'))
            if Version(latestVersion) > Version(self.version):
                updateCheckDialog.ui.versionsTableWidget.setItem(0, 0, QTableWidgetItem(QIcon(QPixmap(':/creepy/exclamation')), ''))
                updateCheckDialog.ui.versionsTableWidget.setItem(0, 2, QTableWidgetItem('Outdated'))
                updateCheckDialog.ui.dlNewVersionLabel.setText('<html><head/><body><p>Download the latest version from <a href="http://www.geocreepy.com"><span style=" text-decoration: underline; color:#0000ff;">geocreepy.com</span></a></p></body></html>')
            else:
                updateCheckDialog.ui.versionsTableWidget.setItem(0, 0, QTableWidgetItem(QIcon(QPixmap(':/creepy/tick')), ''))
                updateCheckDialog.ui.versionsTableWidget.setItem(0, 2, QTableWidgetItem('Up To Date'))
                updateCheckDialog.ui.dlNewVersionLabel.setText('<html><head/><body><p>You are already using the latest version of creepy. </p></body></html>')
            updateCheckDialog.ui.versionsTableWidget.setItem(0, 3, QTableWidgetItem(self.version))
            updateCheckDialog.ui.versionsTableWidget.setItem(0, 4, QTableWidgetItem(latestVersion))
            updateCheckDialog.show()
            updateCheckDialog.exec_()
        except Exception as err:
            mess = str(err)
            self.showWarning(self.tr('Error checking for updates'), mess)

    def showFilterLocationsPointDialog(self):
        filterLocationsPointDialog = FilterLocationsPointDialog()
        filterLocationsPointDialog.ui.mapPage = WebEnginePageCompat()
        myPyObj = filterLocationsPointDialog.pyObj()
        filterLocationsPointDialog.ui.mapPage.mainFrame().addToJavaScriptWindowObject('myPyObj', myPyObj)
        filterLocationsPointDialog.ui.mapPage.mainFrame().setUrl(QUrl(os.path.join(os.getcwd(), 'include', 'mapSetPoint.html')))
        filterLocationsPointDialog.ui.radiusUnitComboBox.insertItem(0, 'km')
        filterLocationsPointDialog.ui.radiusUnitComboBox.insertItem(1, 'm')
        filterLocationsPointDialog.ui.radiusUnitComboBox.activated[str].connect(filterLocationsPointDialog.onUnitChanged)
        filterLocationsPointDialog.ui.webView.setPage(filterLocationsPointDialog.ui.mapPage)
        filterLocationsPointDialog.show()
        if filterLocationsPointDialog.exec_():
            r = filterLocationsPointDialog.ui.radiusSpinBox.value()
            radius = r * 1000 if filterLocationsPointDialog.unit == 'km' else r
            if hasattr(myPyObj, 'lat') and hasattr(myPyObj, 'lng') and radius:
                self.filterLocationsByPoint(myPyObj.lat, myPyObj.lng, radius)

    def showFilterLocationsDateDialog(self):
        filterLocationsDateDialog = FilterLocationsDateDialog()
        filterLocationsDateDialog.ui.endDateCalendarWidget.setMaximumDate(QDate.currentDate())
        filterLocationsDateDialog.show()
        if filterLocationsDateDialog.exec_():
            startDateTime = QDateTime(filterLocationsDateDialog.ui.startDateCalendarWidget.selectedDate(), filterLocationsDateDialog.ui.startDateTimeEdit.time()).toPyDateTime()
            endDateTime = QDateTime(filterLocationsDateDialog.ui.endDateCalendarWidget.selectedDate(), filterLocationsDateDialog.ui.endDateTimeEdit.time()).toPyDateTime()
            if startDateTime > endDateTime:
                self.showWarning(self.tr('Invalid Dates'), self.tr('The start date needs to be before the end date.<p> Please try again ! </p>'))
            else:
                self.filterLocationsByDate(startDateTime, endDateTime)

    def filterLocationsByDate(self, startDate, endDate):
        if not self.currentProject:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project !'))
            self.ui.statusbar.showMessage(self.tr('Please select a project !'))
            return
        for l in self.currentProject.locations:
            l.visible = startDate < l.datetime < endDate
        self.presentLocations([])

    def filterLocationsByPoint(self, lat, lng, radius):
        if not self.currentProject:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project !'))
            self.ui.statusbar.showMessage(self.tr('Please select a project !'))
            return
        for l in self.currentProject.locations:
            if GeneralUtilities.calcDistance(float(lat), float(lng), float(l.latitude), float(l.longitude)) > radius:
                l.visible = False
        self.presentLocations([])

    def removeAllFilters(self):
        if not self.currentProject:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project !'))
            self.ui.statusbar.showMessage(self.tr('Please select a project !'))
            return
        for l in self.currentProject.locations:
            l.visible = True
        self.presentLocations([])

    def showAboutDialog(self):
        aboutDialog = AboutDialog()
        aboutDialog.show()
        if aboutDialog.exec_():
            pass

    def showWarning(self, title, text):
        QMessageBox.warning(self, title, text)

    def toggleHeatMap(self, checked):
        mapFrame = self.ui.webPage.mainFrame()
        if checked:
            mapFrame.evaluateJavaScript('showHeatmap()')
            mapFrame.evaluateJavaScript('hideMarkers()')
        else:
            mapFrame.evaluateJavaScript('showMarkers()')
            mapFrame.evaluateJavaScript('hideHeatmap()')

    def hideMarkers(self):
        mapFrame = self.ui.webPage.mainFrame()
        mapFrame.evaluateJavaScript('hideMarkers()')

    def showMarkers(self):
        mapFrame = self.ui.webPage.mainFrame()
        mapFrame.evaluateJavaScript('showMarkers()')

    def addMarkerToMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(f'addMarker({location.latitude},{location.longitude},"{location.infowindow}")')

    def centerMap(self, mapFrame, location):
        mapFrame.evaluateJavaScript(f'centerMap({location.latitude},{location.longitude})')

    def setMapZoom(self, mapFrame, level):
        mapFrame.evaluateJavaScript(f'setZoom({level})')

    def clearMarkers(self, mapFrame):
        mapFrame.evaluateJavaScript('clearMarkers()')

    def fitMapToMarkers(self, mapFrame):
        """Adjust map view to fit all visible markers"""
        mapFrame.evaluateJavaScript('fitMapToMarkers()')

    def deleteCurrentProject(self, project=None):
        if not project:
            project = self.currentProject
        if project.isAnalysisRunning:
            self.showWarning(self.tr('Cannot Edit Project'), self.tr('Please wait until analysis is finished before performing further actions on the project'))
            return
        projectName = project.projectName + '.db'
        verifyDeleteDialog = VerifyDeleteDialog()
        verifyDeleteDialog.ui.label.setText(verifyDeleteDialog.ui.label.text().replace('@project@', project.projectName))
        verifyDeleteDialog.show()
        if verifyDeleteDialog.exec_():
            project.deleteProject(projectName)
            self.loadProjectsFromStorage()

    def exportProjectCSV(self, project=None, filtering=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project first'))
            self.ui.statusbar.showMessage(self.tr('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.tr('No locations found'), self.tr('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.tr('The selected project has no locations to be exported'))
            return
        fileName, _ = QFileDialog.getSaveFileName(None, self.tr('Save CSV export as...'), os.getcwd(), 'All files (*.*)')
        if fileName:
            try:
                with open(fileName, 'w', newline='', encoding='utf-8') as fileobj:
                    writer = csv.writer(fileobj, quoting=csv.QUOTE_ALL)
                    writer.writerow(('Timestamp', 'Latitude', 'Longitude', 'Location Name', 'Retrieved from', 'Context'))
                    for loc in project.locations:
                        if (filtering and loc.visible) or not filtering:
                            writer.writerow((loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'), loc.latitude, loc.longitude, loc.shortName, loc.plugin, loc.context))
                self.ui.statusbar.showMessage(self.tr('Project Locations have been exported successfully'))
            except Exception as err:
                logger.error(err)
                self.ui.statusbar.showMessage(self.tr('Error saving the export.'))

    def exportProjectKML(self, project=None, filtering=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project first'))
            self.ui.statusbar.showMessage(self.tr('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.tr('No locations found'), self.tr('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.tr('The selected project has no locations to be exported'))
            return

        fileName, _ = QFileDialog.getSaveFileName(None, self.tr('Save KML export as...'), os.getcwd(), 'All files (*.*)')
        if fileName:
            try:
                with open(fileName, 'w', encoding='utf-8') as fileobj:
                    kml = []
                    kml.append('<?xml version="1.0" encoding="UTF-8"?>')
                    kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
                    kml.append('<Document>')
                    kml.append(f'  <name>{id}.kml</name>')
                    for loc in project.locations:
                        if (filtering and loc.visible) or not filtering:
                            kml.append('  <Placemark>')
                            kml.append(f'  <name>{loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z")}</name>')
                            kml.append(f'    <description>{GeneralUtilities.html_escape(loc.context)}</description>')
                            kml.append('    <Point>')
                            kml.append(f'       <coordinates>{loc.longitude}, {loc.latitude}, 0</coordinates>')
                            kml.append('    </Point>')
                            kml.append('  </Placemark>')
                    kml.append('</Document>')
                    kml.append('</kml>')

                    kml_string = '\n'.join(kml)
                    fileobj.write(kml_string)
                self.ui.statusbar.showMessage(self.tr('Project Locations have been exported successfully'))
            except Exception as err:
                logger.error(err)
                self.ui.statusbar.showMessage(self.tr('Error saving the export.'))

    def analyzeProject(self, project=None):
        '''
        This is called when the user clicks on "Analyze Target". It starts the background thread that
        analyzes targets and returns locations
        '''
        if not project:
            project = self.currentProject
        if project:
            if project.isAnalysisRunning:
                self.showWarning(self.tr('Cannot Edit Project'), self.tr('Please wait until analysis is finished before performing further actions on the project'))
                return
            self.ui.statusbar.showMessage(self.tr('Analyzing project for locations. Please wait...'))
            project.isAnalysisRunning = True
            self.analyzeProjectThreadInstance = self.analyzeProjectThread(project)
            self.analyzeProjectThreadInstance.locations_signal.connect(self.projectAnalysisFinished)
            self.analyzeProjectThreadInstance.start()
        else:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project !'))
        self.loadConfiguredPlugins()

    def projectAnalysisFinished(self, project):
        '''
        Called when the analysis thread finishes. It saves the project with the locations and draws the map
        '''
        self.ui.statusbar.showMessage(self.tr('Project Analysis complete !'))
        projectNode = ProjectNode(project.projectName, project)
        locationsNode = LocationsNode(self.tr('Locations'), projectNode)
        project.isAnalysisRunning = False
        project.storeProject(projectNode)
        '''
        If the analysis produced no results whatsoever, inform the user
        '''
        if not project.locations:
            self.showWarning(self.tr('No Locations Found'), self.tr('We could not find any locations for the analyzed project'))
        else:
            self.presentLocations(project.locations)

    def presentLocations(self, locations):
        '''
        Also called when the user clicks on "Analyze Target". It redraws the map and populates the location list
        '''
        if not locations:
            if not self.currentProject:
                self.showWarning(self.tr('No project selected'), self.tr('Please select a project !'))
                self.ui.statusbar.showMessage(self.tr('Please select a project !'))
                return
            else:
                locations = self.currentProject.locations
        mapFrame = self.ui.webPage.mainFrame()
        self.clearMarkers(mapFrame)
        visibleLocations = []
        if locations:
            for location in locations:
                if location.visible:
                    visibleLocations.append(location)
                    self.addMarkerToMap(mapFrame, location)
            if visibleLocations:
                # If only one location, center on it with high zoom
                if len(visibleLocations) == 1:
                    self.centerMap(mapFrame, visibleLocations[0])
                    self.setMapZoom(mapFrame, 15)
                else:
                    # Use JavaScript to fit bounds around all markers
                    self.fitMapToMarkers(mapFrame)
        else:
            self.showWarning(self.tr('No locations found'), self.tr('No locations found for the selected project.'))
            self.ui.statusbar.showMessage(self.tr('No locations found for the selected project.'))

        self.locationsTableModel = LocationsTableModel(visibleLocations)
        self.ui.locationsTableView.setModel(self.locationsTableModel)
        self.ui.locationsTableView.clicked.connect(self.updateCurrentLocationDetails)
        self.ui.locationsTableView.activated.connect(self.updateCurrentLocationDetails)
        self.ui.locationsTableView.doubleClicked.connect(self.doubleClickLocationItem)
        self.ui.locationsTableView.resizeColumnsToContents()

    def doubleClickLocationItem(self, index):
        location = self.locationsTableModel.locations[index.row()]
        mapFrame = self.ui.webPage.mainFrame()
        self.centerMap(mapFrame, location)
        self.setMapZoom(mapFrame, 18)

    def updateCurrentLocationDetails(self, index):
        '''
        Called when the user clicks on a location from the location list. It updates the information
        displayed on the Current Target Details Window
        '''
        location = self.locationsTableModel.locations[index.row()]
        self.ui.currentTargetDetailsLocationValue.setText(location.shortName)
        self.ui.currentTargetDetailsDateValue.setText(location.datetime.strftime('%Y-%m-%d %H:%M:%S %z'))
        self.ui.currentTargetDetailsSourceValue.setText(location.plugin)
        self.ui.currentTargetDetailsContextValue.setText(location.context)

    def changeMainWidgetPage(self, pageType):
        '''
        Changes what is shown in the main window between the map mode and the analysis mode
        '''
        if pageType == 'map':
            self.ui.centralStackedWidget.setCurrentIndex(0)
        else:
            self.ui.centralStackedWidget.setCurrentIndex(1)

    def wizardButtonPressed(self, plugin):
        '''
        This metod calls the wizard of the selected plugin and then reads again the configuration options from file
        for that specific plugin. This happens in order to reflect any changes the wizard might have made to the configuration
        options.
        '''
        plugin.plugin_object.runConfigWizard()
        self.pluginsConfigurationDialog.close()
        self.showPluginsConfigurationDialog()

    def showPluginsConfigurationDialog(self):
        '''
        Reads the configuration options for all the plugins, builds the relevant UI items and adds them to the dialog
        '''
        # Show the stackWidget
        self.pluginsConfigurationDialog = PluginsConfigurationDialog()
        self.pluginsConfigurationDialog.ui.ConfigurationDetails = QStackedWidget(self.pluginsConfigurationDialog)
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setGeometry(QRect(260, 10, 511, 561))
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setObjectName('ConfigurationDetails')
        pl = []
        for plugin in sorted(self.pluginsConfigurationDialog.PluginManager.getAllPlugins(), key=lambda x: x.name):
            pl.append(plugin)
            '''
            Build the configuration page from the available configuration options
            and add the page to the stackwidget
            '''
            page = QWidget()
            page.setObjectName('page_' + plugin.name)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            layout = QVBoxLayout()
            titleLabel = QLabel(plugin.name + self.tr(' Configuration Options'))
            layout.addWidget(titleLabel)
            vboxWidget = QWidget()
            vboxWidget.setObjectName('vboxwidget_container_' + plugin.name)
            vbox = QGridLayout()
            vbox.setObjectName('vbox_container_' + plugin.name)
            gridLayoutRowIndex = 0
            '''
            Load the String options first
            '''
            pluginStringOptions = plugin.plugin_object.readConfiguration('string_options')[1]
            if pluginStringOptions is not None:
                for idx, item in enumerate(pluginStringOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    label = QLabel()
                    label.setObjectName('string_label_' + item)
                    label.setText(itemLabel)
                    vbox.addWidget(label, idx, 0)
                    value = QLineEdit()
                    if item.startswith('hidden_'):
                        value.setEchoMode(QLineEdit.Password)
                    value.setObjectName('string_value_' + item)
                    value.setText(pluginStringOptions[item])
                    vbox.addWidget(value, idx, 1)
                    gridLayoutRowIndex = idx + 1
            '''
            Load the boolean options
            '''
            pluginBooleanOptions = plugin.plugin_object.readConfiguration('boolean_options')[1]
            if pluginBooleanOptions is not None:
                for idx, item in enumerate(pluginBooleanOptions.keys()):
                    itemLabel = plugin.plugin_object.getLabelForKey(item)
                    cb = QCheckBox(itemLabel)
                    cb.setObjectName('boolean_label_' + item)
                    if pluginBooleanOptions[item] == 'True':
                        cb.toggle()
                    vbox.addWidget(cb, gridLayoutRowIndex + idx, 0)
                    gridLayoutRowIndex += 1
            '''
            Add the wizard button if the plugin has a configuration wizard
            '''
            if plugin.plugin_object.hasWizard:
                wizardButton = QPushButton(self.tr('Run Configuration Wizard'))
                wizardButton.setObjectName('wizardButton_' + plugin.name)
                wizardButton.setToolTip(self.tr('Click here to run the configuration wizard for the plugin'))
                wizardButton.resize(wizardButton.sizeHint())
                wizardButton.clicked.connect(functools.partial(self.wizardButtonPressed, plugin))
                vbox.addWidget(wizardButton, gridLayoutRowIndex + 1, 0)
            vboxWidget.setLayout(vbox)
            scroll.setWidget(vboxWidget)
            layout.addWidget(scroll)
            layout.addStretch(1)
            pluginsConfigButtonContainer = QHBoxLayout()
            checkConfigButton = QPushButton(self.tr('Test Plugin Configuration'))
            checkConfigButton.setObjectName('checkConfigButton_' + plugin.name)
            checkConfigButton.setToolTip(self.tr('Click here to test the plugin\'s configuration'))
            checkConfigButton.resize(checkConfigButton.sizeHint())
            checkConfigButton.clicked.connect(functools.partial(self.pluginsConfigurationDialog.checkPluginConfiguration, plugin))
            applyConfigButton = QPushButton(self.tr('Apply Configuration'))
            applyConfigButton.setObjectName('applyConfigButton_' + plugin.name)
            applyConfigButton.setToolTip(self.tr('Click here to save the plugin\'s configuration options'))
            applyConfigButton.resize(applyConfigButton.sizeHint())
            applyConfigButton.clicked.connect(self.pluginsConfigurationDialog.saveConfiguration)
            pluginsConfigButtonContainer.addStretch(1)
            pluginsConfigButtonContainer.addWidget(applyConfigButton)
            pluginsConfigButtonContainer.addWidget(checkConfigButton)
            layout.addLayout(pluginsConfigButtonContainer)
            page.setLayout(layout)
            self.pluginsConfigurationDialog.ui.ConfigurationDetails.addWidget(page)
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(0)
        self.PluginConfigurationListModel = PluginConfigurationListModel(pl, self)
        self.PluginConfigurationListModel.checkPluginConfiguration()
        self.pluginsConfigurationDialog.ui.PluginsList.setModel(self.PluginConfigurationListModel)
        self.pluginsConfigurationDialog.ui.PluginsList.clicked.connect(self.changePluginConfigurationPage)
        if self.pluginsConfigurationDialog.exec_():
            self.pluginsConfigurationDialog.saveConfiguration()
        self.loadConfiguredPlugins()

    def changePluginConfigurationPage(self, modelIndex):
        '''
        Changes the page in the PluginConfiguration Dialog depending on which plugin is currently
        selected in the plugin list
        '''
        self.pluginsConfigurationDialog.ui.ConfigurationDetails.setCurrentIndex(modelIndex.row())

    def showPersonProjectWizard(self):
        '''
            # locationsNode = LocationsNode('Locations', projectNode)
        '''
        personProjectWizard = PersonProjectWizard()
        personProjectWizard.ProjectWizardPluginListModel = ProjectWizardPluginListModel(personProjectWizard.loadConfiguredPlugins(), self)
        personProjectWizard.ui.personProjectAvailablePluginsListView.setModel(personProjectWizard.ProjectWizardPluginListModel)
        personProjectWizard.ui.personProjectSearchButton.clicked.connect(personProjectWizard.searchForTargets)
        # Creating it here so it becomes available globally in all functions
        personProjectWizard.ProjectWizardSelectedTargetsTable = ProjectWizardSelectedTargetsTable([], self)
        if personProjectWizard.exec_():
            project = Project()
            project.projectName = personProjectWizard.ui.personProjectNameValue.text()
            project.projectKeywords = [keyword.strip() for keyword in personProjectWizard.ui.personProjectKeywordsValue.text().split(',')]
            project.projectDescription = personProjectWizard.ui.personProjectDescriptionValue.toPlainText()
            project.enabledPlugins = personProjectWizard.readSearchConfiguration()
            project.dateCreated = datetime.datetime.now()
            project.dateEdited = datetime.datetime.now()
            project.locations = []
            project.analysis = None
            project.isAnalysisRunning = False
            project.viewSettings = {}  # Fixed typo here
            project.selectedTargets = personProjectWizard.selectedTargets
            projectNode = ProjectNode(project.projectName, project)

    def loadProjectsFromStorage(self):
        """Load projects from storage and populate the projects tree."""
        try:
            logger.info("Loading projects from storage...")
            
            # Get list of all projects
            from models.Project import Project
            projectsList = Project.getProjectsList()
            
            # Create a root node for the project tree
            self.projectsRootNode = ProjectTreeNode('Projects')
            
            # Add projects to the tree
            for project_data in projectsList:
                try:
                    # Load the project
                    project_path = project_data['path']
                    project = Project(project_path)
                    
                    # Create a tree node for the project
                    projectNode = ProjectNode(project.projectName, project)
                    
                    # Add locations node
                    locationsNode = LocationsNode('Locations', projectNode)
                    
                    # Add analysis node
                    analysisNode = AnalysisNode('Analysis Results', projectNode)
                    
                    # Add project node to root
                    self.projectsRootNode.addChild(projectNode)
                    
                    # Add project to list
                    self.projectsList.append(project)
                    
                except Exception as e:
                    logger.error(f"Error loading project {project_data['name']}: {str(e)}")
            
            # Create tree model
            self.projectTreeModel = ProjectTreeModel(self.projectsRootNode)
            
            # Set model on the view
            if hasattr(self.ui, 'projectsTreeView'):
                self.ui.projectsTreeView.setModel(self.projectTreeModel)
                self.ui.projectsTreeView.setHeaderHidden(True)
                self.ui.projectsTreeView.expandAll()
                
                # Connect selection signals
                self.ui.projectsTreeView.clicked.connect(self.projectNodeSelected)
            else:
                logger.warning("No projectsTreeView found in UI")
                
            logger.info(f"Loaded {len(self.projectsList)} projects")
        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")
            self.showWarning("Error Loading Projects", f"Failed to load projects: {str(e)}")

    def projectNodeSelected(self, index):
        """Handle selection of a node in the projects tree."""
        try:
            node = index.internalPointer()
            if node and node.nodeType() == 'PROJECT':
                # Project node selected
                self.currentProject = node.project
                logger.info(f"Selected project: {self.currentProject.projectName}")
                
                # Enable project-specific actions
                self.ui.actionAnalyzeCurrentProject.setEnabled(True)
                self.ui.actionReanalyzeCurrentProject.setEnabled(True)
                self.ui.actionDrawCurrentProject.setEnabled(True)
                self.ui.actionExportCSV.setEnabled(True)
                self.ui.actionExportKML.setEnabled(True)
                self.ui.actionDeleteCurrentProject.setEnabled(True)
                
                # Update the status bar
                self.ui.statusbar.showMessage(f"Project selected: {self.currentProject.projectName}")
                
                # If the project has locations, present them
                if self.currentProject.locations:
                    self.presentLocations(self.currentProject.locations)
            elif node and node.nodeType() == 'LOCATIONS':
                # Locations node selected
                if node.parent() and node.parent().nodeType() == 'PROJECT':
                    self.currentProject = node.parent().project
                    self.presentLocations(self.currentProject.locations)
            elif node and node.nodeType() == 'ANALYSIS':
                # Analysis node selected
                if node.parent() and node.parent().nodeType() == 'PROJECT':
                    self.currentProject = node.parent().project
                    # Show analysis view
                    self.changeMainWidgetPage('analysis')
        except Exception as e:
            logger.error(f"Error handling project selection: {str(e)}")

# Entry point of the application
def main():
    try:
        # Fix Tkinter compatibility issues if any Tkinter UI is used
        fix_tkinter_buttons_in_pyqt()
        
        # Set application metadata
        app.setApplicationName("CreepyAI")
        app.setOrganizationName("CreepyAI")
        app.setOrganizationDomain("geocreepy.com")
        
        # Apply stylesheet if available
        style_path = resource_loader.get_resource_path('styles', 'main')
        if style_path:
            with open(style_path, 'r') as f:
                app.setStyleSheet(f.read())
        
        # Create and show the main window
        mainWindow = MainWindow()
        mainWindow.show()
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        # Show error dialog if GUI is available
        try:
            QMessageBox.critical(None, "Critical Error", 
                              f"An unhandled error occurred:\n{str(e)}\n\nPlease check the logs for details.")
        except:
            pass
        return 1

if __name__ == "__main__":
    from utilities.Initialization import AppInitializer

    initializer = AppInitializer()
    initializer.pre_init()
    app = initializer.init_app()
    initializer.post_init()

    # Create and show the main window
    mainWindow = MainWindow()
    mainWindow.show()

    # Start the application event loop
    sys.exit(app.exec_())
