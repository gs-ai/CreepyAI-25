from PyQt5.QtCore import Qt, QSize, QRect, QMetaObject
from PyQt5.QtWidgets import (QMainWindow, QAction, QWidget, QMenuBar, QMenu, 
                            QStatusBar, QDockWidget, QToolBar, QStackedWidget, 
                            QVBoxLayout, QHBoxLayout, QTableView, QLabel, 
                            QLineEdit, QTextEdit, QSplitter)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebKitWidgets import QWebView
import os


class Ui_CreepyMainWindow(object):
    def setupUi(self, CreepyMainWindow):
        """Set up the UI for the main window."""
        CreepyMainWindow.setObjectName("CreepyMainWindow")
        CreepyMainWindow.resize(1200, 800)
        CreepyMainWindow.setWindowTitle("CreepyAI - Geolocation OSINT Tool")
        CreepyMainWindow.setWindowIcon(QIcon(os.path.join(os.getcwd(), "include", "creepy.png")))
        
        # Central widget setup
        self.centralWidget = QWidget(CreepyMainWindow)
        self.centralWidget.setObjectName("centralWidget")
        CreepyMainWindow.setCentralWidget(self.centralWidget)
        
        # Central widget layout
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.setSpacing(0)
        
        # Create the stacked widget for map view and analysis view
        self.centralStackedWidget = QStackedWidget(self.centralWidget)
        self.centralStackedWidget.setObjectName("centralStackedWidget")
        
        # Map page
        self.mapPage = QWidget()
        self.mapPage.setObjectName("mapPage")
        self.mapLayout = QVBoxLayout(self.mapPage)
        self.mapLayout.setContentsMargins(0, 0, 0, 0)
        self.mapWebView = QWebView(self.mapPage)
        self.mapWebView.setObjectName("mapWebView")
        self.mapLayout.addWidget(self.mapWebView)
        self.centralStackedWidget.addWidget(self.mapPage)
        
        # Analysis page
        self.analysisPage = QWidget()
        self.analysisPage.setObjectName("analysisPage")
        self.analysisLayout = QVBoxLayout(self.analysisPage)
        self.analysisLayout.setContentsMargins(0, 0, 0, 0)
        self.analysisLabel = QLabel("Analysis View (Placeholder)")
        self.analysisLabel.setAlignment(Qt.AlignCenter)
        self.analysisLayout.addWidget(self.analysisLabel)
        self.centralStackedWidget.addWidget(self.analysisPage)
        
        # Add stacked widget to central layout
        self.centralLayout.addWidget(self.centralStackedWidget)
        
        # Create menu bar
        self.menubar = QMenuBar(CreepyMainWindow)
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        self.menubar.setObjectName("menubar")
        
        # File menu
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setTitle("File")
        self.menuFile.setObjectName("menuFile")
        
        # View menu
        self.menuView = QMenu(self.menubar)
        self.menuView.setTitle("View")
        self.menuView.setObjectName("menuView")
        
        # Project menu
        self.menuProject = QMenu(self.menubar)
        self.menuProject.setTitle("Project")
        self.menuProject.setObjectName("menuProject")
        
        # Filter menu
        self.menuFilter = QMenu(self.menubar)
        self.menuFilter.setTitle("Filter")
        self.menuFilter.setObjectName("menuFilter")
        
        # Export menu
        self.menuExport = QMenu(self.menubar)
        self.menuExport.setTitle("Export")
        self.menuExport.setObjectName("menuExport")
        
        # Help menu
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setTitle("Help")
        self.menuHelp.setObjectName("menuHelp")
        
        CreepyMainWindow.setMenuBar(self.menubar)
        
        # Create status bar
        self.statusbar = QStatusBar(CreepyMainWindow)
        self.statusbar.setObjectName("statusbar")
        CreepyMainWindow.setStatusBar(self.statusbar)
        
        # Create dock widgets
        
        # Projects dock
        self.dockWProjects = QDockWidget("Projects", CreepyMainWindow)
        self.dockWProjects.setObjectName("dockWProjects")
        self.dockWProjects.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dockWidgetContentsProjects = QWidget()
        self.dockWidgetContentsProjects.setObjectName("dockWidgetContentsProjects")
        self.dockWProjectsLayout = QVBoxLayout(self.dockWidgetContentsProjects)
        
        # Projects tree view
        self.treeViewProjects = QTableView(self.dockWidgetContentsProjects)
        self.treeViewProjects.setObjectName("treeViewProjects")
        self.treeViewProjects.setEditTriggers(QTableView.NoEditTriggers)
        self.dockWProjectsLayout.addWidget(self.treeViewProjects)
        
        self.dockWProjects.setWidget(self.dockWidgetContentsProjects)
        CreepyMainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWProjects)
        
        # Locations list dock
        self.dockWLocationsList = QDockWidget("Locations", CreepyMainWindow)
        self.dockWLocationsList.setObjectName("dockWLocationsList")
        self.dockWLocationsList.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dockWidgetContentsLocationsList = QWidget()
        self.dockWidgetContentsLocationsList.setObjectName("dockWidgetContentsLocationsList")
        self.dockWLocationsListLayout = QVBoxLayout(self.dockWidgetContentsLocationsList)
        
        # Locations table view
        self.locationsTableView = QTableView(self.dockWidgetContentsLocationsList)
        self.locationsTableView.setObjectName("locationsTableView")
        self.locationsTableView.setEditTriggers(QTableView.NoEditTriggers)
        self.dockWLocationsListLayout.addWidget(self.locationsTableView)
        
        self.dockWLocationsList.setWidget(self.dockWidgetContentsLocationsList)
        CreepyMainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWLocationsList)
        
        # Current location details dock
        self.dockWCurrentLocationDetails = QDockWidget("Location Details", CreepyMainWindow)
        self.dockWCurrentLocationDetails.setObjectName("dockWCurrentLocationDetails")
        self.dockWCurrentLocationDetails.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.dockWidgetContentsLocationDetails = QWidget()
        self.dockWidgetContentsLocationDetails.setObjectName("dockWidgetContentsLocationDetails")
        self.dockWLocationDetailsLayout = QVBoxLayout(self.dockWidgetContentsLocationDetails)
        
        # Location details grid
        self.locationDetailsGrid = QVBoxLayout()
        
        # Location field
        self.locationHBox = QHBoxLayout()
        self.currentTargetDetailsLocationLabel = QLabel("Location:")
        self.currentTargetDetailsLocationValue = QLineEdit()
        self.currentTargetDetailsLocationValue.setReadOnly(True)
        self.locationHBox.addWidget(self.currentTargetDetailsLocationLabel)
        self.locationHBox.addWidget(self.currentTargetDetailsLocationValue)
        self.locationDetailsGrid.addLayout(self.locationHBox)
        
        # Date field
        self.dateHBox = QHBoxLayout()
        self.currentTargetDetailsDateLabel = QLabel("Date:")
        self.currentTargetDetailsDateValue = QLineEdit()
        self.currentTargetDetailsDateValue.setReadOnly(True)
        self.dateHBox.addWidget(self.currentTargetDetailsDateLabel)
        self.dateHBox.addWidget(self.currentTargetDetailsDateValue)
        self.locationDetailsGrid.addLayout(self.dateHBox)
        
        # Source field
        self.sourceHBox = QHBoxLayout()
        self.currentTargetDetailsSourceLabel = QLabel("Source:")
        self.currentTargetDetailsSourceValue = QLineEdit()
        self.currentTargetDetailsSourceValue.setReadOnly(True)
        self.sourceHBox.addWidget(self.currentTargetDetailsSourceLabel)
        self.sourceHBox.addWidget(self.currentTargetDetailsSourceValue)
        self.locationDetailsGrid.addLayout(self.sourceHBox)
        
        # Context field
        self.contextHBox = QHBoxLayout()
        self.currentTargetDetailsContextLabel = QLabel("Context:")
        self.currentTargetDetailsContextValue = QTextEdit()
        self.currentTargetDetailsContextValue.setReadOnly(True)
        self.contextHBox.addWidget(self.currentTargetDetailsContextLabel)
        self.contextHBox.addWidget(self.currentTargetDetailsContextValue)
        self.locationDetailsGrid.addLayout(self.contextHBox)
        
        self.dockWLocationDetailsLayout.addLayout(self.locationDetailsGrid)
        self.dockWCurrentLocationDetails.setWidget(self.dockWidgetContentsLocationDetails)
        CreepyMainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.dockWCurrentLocationDetails)
        
        # Create actions
        
        # File menu actions
        self.actionExit = QAction("Exit", CreepyMainWindow)
        self.actionExit.setStatusTip("Exit the application")
        self.actionExit.setObjectName("actionExit")
        
        # Project menu actions
        self.actionNewPersonProject = QAction("New Person Project", CreepyMainWindow)
        self.actionNewPersonProject.setStatusTip("Create a new person project")
        self.actionNewPersonProject.setObjectName("actionNewPersonProject")
        
        self.actionAnalyzeCurrentProject = QAction("Analyze Project", CreepyMainWindow)
        self.actionAnalyzeCurrentProject.setStatusTip("Analyze the selected project")
        self.actionAnalyzeCurrentProject.setObjectName("actionAnalyzeCurrentProject")
        
        self.actionReanalyzeCurrentProject = QAction("Reanalyze Project", CreepyMainWindow)
        self.actionReanalyzeCurrentProject.setStatusTip("Reanalyze the selected project")
        self.actionReanalyzeCurrentProject.setObjectName("actionReanalyzeCurrentProject")
        
        self.actionDrawCurrentProject = QAction("Draw Project on Map", CreepyMainWindow)
        self.actionDrawCurrentProject.setStatusTip("Draw the selected project on the map")
        self.actionDrawCurrentProject.setObjectName("actionDrawCurrentProject")
        
        self.actionDeleteCurrentProject = QAction("Delete Project", CreepyMainWindow)
        self.actionDeleteCurrentProject.setStatusTip("Delete the selected project")
        self.actionDeleteCurrentProject.setObjectName("actionDeleteCurrentProject")
        
        self.actionPluginsConfiguration = QAction("Plugins Configuration", CreepyMainWindow)
        self.actionPluginsConfiguration.setStatusTip("Configure the plugins")
        self.actionPluginsConfiguration.setObjectName("actionPluginsConfiguration")
        
        # Filter menu actions
        self.actionFilterLocationsDate = QAction("Filter by Date", CreepyMainWindow)
        self.actionFilterLocationsDate.setStatusTip("Filter locations by date")
        self.actionFilterLocationsDate.setObjectName("actionFilterLocationsDate")
        
        self.actionFilterLocationsPosition = QAction("Filter by Position", CreepyMainWindow)
        self.actionFilterLocationsPosition.setStatusTip("Filter locations by position")
        self.actionFilterLocationsPosition.setObjectName("actionFilterLocationsPosition")
        
        self.actionRemoveFilters = QAction("Remove All Filters", CreepyMainWindow)
        self.actionRemoveFilters.setStatusTip("Remove all filters")
        self.actionRemoveFilters.setObjectName("actionRemoveFilters")
        
        self.actionShowHeatMap = QAction("Show Heat Map", CreepyMainWindow)
        self.actionShowHeatMap.setStatusTip("Show locations as a heat map")
        self.actionShowHeatMap.setCheckable(True)
        self.actionShowHeatMap.setObjectName("actionShowHeatMap")
        
        # Export menu actions
        self.actionExportCSV = QAction("Export to CSV", CreepyMainWindow)
        self.actionExportCSV.setStatusTip("Export locations to CSV file")
        self.actionExportCSV.setObjectName("actionExportCSV")
        
        self.actionExportKML = QAction("Export to KML", CreepyMainWindow)
        self.actionExportKML.setStatusTip("Export locations to KML file")
        self.actionExportKML.setObjectName("actionExportKML")
        
        self.actionExportFilteredCSV = QAction("Export Filtered to CSV", CreepyMainWindow)
        self.actionExportFilteredCSV.setStatusTip("Export filtered locations to CSV file")
        self.actionExportFilteredCSV.setObjectName("actionExportFilteredCSV")
        
        self.actionExportFilteredKML = QAction("Export Filtered to KML", CreepyMainWindow)
        self.actionExportFilteredKML.setStatusTip("Export filtered locations to KML file")
        self.actionExportFilteredKML.setObjectName("actionExportFilteredKML")
        
        # Help menu actions
        self.actionAbout = QAction("About", CreepyMainWindow)
        self.actionAbout.setStatusTip("Show the application's About box")
        self.actionAbout.setObjectName("actionAbout")
        
        self.actionCheckUpdates = QAction("Check for Updates", CreepyMainWindow)
        self.actionCheckUpdates.setStatusTip("Check if updates are available")
        self.actionCheckUpdates.setObjectName("actionCheckUpdates")
        
        self.actionReportProblem = QAction("Report Problem", CreepyMainWindow)
        self.actionReportProblem.setStatusTip("Report a problem with the application")
        self.actionReportProblem.setObjectName("actionReportProblem")
        
        # Add actions to menus
        self.menuFile.addAction(self.actionPluginsConfiguration)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
        self.menuProject.addAction(self.actionNewPersonProject)
        self.menuProject.addAction(self.actionAnalyzeCurrentProject)
        self.menuProject.addAction(self.actionReanalyzeCurrentProject)
        self.menuProject.addAction(self.actionDrawCurrentProject)
        self.menuProject.addAction(self.actionDeleteCurrentProject)
        
        self.menuFilter.addAction(self.actionFilterLocationsDate)
        self.menuFilter.addAction(self.actionFilterLocationsPosition)
        self.menuFilter.addAction(self.actionRemoveFilters)
        self.menuFilter.addSeparator()
        self.menuFilter.addAction(self.actionShowHeatMap)
        
        self.menuExport.addAction(self.actionExportCSV)
        self.menuExport.addAction(self.actionExportKML)
        self.menuExport.addAction(self.actionExportFilteredCSV)
        self.menuExport.addAction(self.actionExportFilteredKML)
        
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionCheckUpdates)
        self.menuHelp.addAction(self.actionReportProblem)
        
        # Add menus to menu bar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuProject.menuAction())
        self.menubar.addAction(self.menuFilter.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        # Create toolbar
        self.mainToolBar = QToolBar(CreepyMainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        self.mainToolBar.setMovable(False)
        CreepyMainWindow.addToolBar(Qt.TopToolBarArea, self.mainToolBar)
        
        # Add actions to toolbar
        self.mainToolBar.addAction(self.actionNewPersonProject)
        self.mainToolBar.addAction(self.actionAnalyzeCurrentProject)
        self.mainToolBar.addAction(self.actionDrawCurrentProject)
        self.mainToolBar.addAction(self.actionShowHeatMap)
        
        # Set initial state
        self.centralStackedWidget.setCurrentIndex(0)
        
        QMetaObject.connectSlotsByName(CreepyMainWindow)
