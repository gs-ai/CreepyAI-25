from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QTreeView, QTableView, QStackedWidget, QDockWidget, QMenuBar, QMenu, QAction, QStatusBar, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox, QFormLayout

class Ui_CreepyMainWindow(object):
    def setupUi(self, CreepyMainWindow):
        CreepyMainWindow.setObjectName("CreepyMainWindow")
        CreepyMainWindow.resize(1200, 800)
        
        self.centralWidget = QWidget(CreepyMainWindow)
        self.centralWidget.setObjectName("centralWidget")
        
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setObjectName("centralLayout")
        
        self.centralStackedWidget = QStackedWidget(self.centralWidget)
        self.centralStackedWidget.setObjectName("centralStackedWidget")
        
        self.mapPage = QWidget()
        self.mapPage.setObjectName("mapPage")
        self.mapLayout = QVBoxLayout(self.mapPage)
        self.mapLayout.setObjectName("mapLayout")
        
        self.mapWebView = QWebEngineView(self.mapPage)
        self.mapWebView.setObjectName("mapWebView")
        self.mapLayout.addWidget(self.mapWebView)
        
        self.centralStackedWidget.addWidget(self.mapPage)
        
        self.analysisPage = QWidget()
        self.analysisPage.setObjectName("analysisPage")
        self.analysisLayout = QVBoxLayout(self.analysisPage)
        self.analysisLayout.setObjectName("analysisLayout")
        
        self.analysisLabel = QLabel("Analysis Results", self.analysisPage)
        self.analysisLayout.addWidget(self.analysisLabel)
        
        self.centralStackedWidget.addWidget(self.analysisPage)
        
        self.centralLayout.addWidget(self.centralStackedWidget)
        
        CreepyMainWindow.setCentralWidget(self.centralWidget)
        
        self.dockWProjects = QDockWidget(CreepyMainWindow)
        self.dockWProjects.setObjectName("dockWProjects")
        self.dockWProjects.setWindowTitle("Projects")
        
        self.projectsTreeView = QTreeView(self.dockWProjects)
        self.projectsTreeView.setObjectName("projectsTreeView")
        self.dockWProjects.setWidget(self.projectsTreeView)
        
        CreepyMainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWProjects)
        
        self.dockWLocationsList = QDockWidget(CreepyMainWindow)
        self.dockWLocationsList.setObjectName("dockWLocationsList")
        self.dockWLocationsList.setWindowTitle("Locations")
        
        self.locationsTableView = QTableView(self.dockWLocationsList)
        self.locationsTableView.setObjectName("locationsTableView")
        self.dockWLocationsList.setWidget(self.locationsTableView)
        
        CreepyMainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWLocationsList)
        
        self.dockWCurrentLocationDetails = QDockWidget(CreepyMainWindow)
        self.dockWCurrentLocationDetails.setObjectName("dockWCurrentLocationDetails")
        self.dockWCurrentLocationDetails.setWindowTitle("Current Location Details")
        
        self.currentLocationDetailsWidget = QWidget(self.dockWCurrentLocationDetails)
        self.currentLocationDetailsLayout = QFormLayout(self.currentLocationDetailsWidget)
        
        self.currentTargetDetailsLocationLabel = QLabel("Location:", self.currentLocationDetailsWidget)
        self.currentTargetDetailsLocationValue = QLabel("", self.currentLocationDetailsWidget)
        self.currentLocationDetailsLayout.addRow(self.currentTargetDetailsLocationLabel, self.currentTargetDetailsLocationValue)
        
        self.currentTargetDetailsDateLabel = QLabel("Date:", self.currentLocationDetailsWidget)
        self.currentTargetDetailsDateValue = QLabel("", self.currentLocationDetailsWidget)
        self.currentLocationDetailsLayout.addRow(self.currentTargetDetailsDateLabel, self.currentTargetDetailsDateValue)
        
        self.currentTargetDetailsSourceLabel = QLabel("Source:", self.currentLocationDetailsWidget)
        self.currentTargetDetailsSourceValue = QLabel("", self.currentLocationDetailsWidget)
        self.currentLocationDetailsLayout.addRow(self.currentTargetDetailsSourceLabel, self.currentTargetDetailsSourceValue)
        
        self.currentTargetDetailsContextLabel = QLabel("Context:", self.currentLocationDetailsWidget)
        self.currentTargetDetailsContextValue = QLabel("", self.currentLocationDetailsWidget)
        self.currentLocationDetailsLayout.addRow(self.currentTargetDetailsContextLabel, self.currentTargetDetailsContextValue)
        
        self.dockWCurrentLocationDetails.setWidget(self.currentLocationDetailsWidget)
        
        CreepyMainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWCurrentLocationDetails)
        
        self.menuBar = QMenuBar(CreepyMainWindow)
        self.menuBar.setObjectName("menuBar")
        
        self.menuFile = QMenu("File", self.menuBar)
        self.menuView = QMenu("View", self.menuBar)
        self.menuHelp = QMenu("Help", self.menuBar)
        
        self.actionNewPersonProject = QAction("New Person Project", CreepyMainWindow)
        self.actionAnalyzeCurrentProject = QAction("Analyze Current Project", CreepyMainWindow)
        self.actionReanalyzeCurrentProject = QAction("Reanalyze Current Project", CreepyMainWindow)
        self.actionDrawCurrentProject = QAction("Draw Current Project", CreepyMainWindow)
        self.actionExportCSV = QAction("Export CSV", CreepyMainWindow)
        self.actionExportKML = QAction("Export KML", CreepyMainWindow)
        self.actionExportFilteredCSV = QAction("Export Filtered CSV", CreepyMainWindow)
        self.actionExportFilteredKML = QAction("Export Filtered KML", CreepyMainWindow)
        self.actionDeleteCurrentProject = QAction("Delete Current Project", CreepyMainWindow)
        self.actionFilterLocationsDate = QAction("Filter Locations by Date", CreepyMainWindow)
        self.actionFilterLocationsPosition = QAction("Filter Locations by Position", CreepyMainWindow)
        self.actionRemoveFilters = QAction("Remove All Filters", CreepyMainWindow)
        self.actionShowHeatMap = QAction("Show Heat Map", CreepyMainWindow)
        self.actionShowHeatMap.setCheckable(True)
        self.actionPluginsConfiguration = QAction("Plugins Configuration", CreepyMainWindow)
        self.actionReportProblem = QAction("Report Problem", CreepyMainWindow)
        self.actionAbout = QAction("About", CreepyMainWindow)
        self.actionCheckUpdates = QAction("Check for Updates", CreepyMainWindow)
        self.actionExit = QAction("Exit", CreepyMainWindow)
        
        self.menuFile.addAction(self.actionNewPersonProject)
        self.menuFile.addAction(self.actionExit)
        
        self.menuView.addAction(self.dockWProjects.toggleViewAction())
        self.menuView.addAction(self.dockWLocationsList.toggleViewAction())
        self.menuView.addAction(self.dockWCurrentLocationDetails.toggleViewAction())
        
        self.menuHelp.addAction(self.actionReportProblem)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionCheckUpdates)
        
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        
        CreepyMainWindow.setMenuBar(self.menuBar)
        
        self.statusBar = QStatusBar(CreepyMainWindow)
        CreepyMainWindow.setStatusBar(self.statusBar)
        
        self.retranslateUi(CreepyMainWindow)
        
    def retranslateUi(self, CreepyMainWindow):
        _translate = QCoreApplication.translate
        CreepyMainWindow.setWindowTitle(_translate("CreepyMainWindow", "CreepyAI"))
