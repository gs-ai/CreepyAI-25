# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\creepy.ui'
#
# Created: Fri Jan 31 15:55:30 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

<<<<<<< HEAD
from PyQt5 import QtCore, QtGui, QtWidgets
from creepy.resources.icons import Icons
from PyQt5.QtWebKitWidgets import QWebView
=======
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
>>>>>>> gs-ai-patch-1

try:
    _fromUtf8 = lambda s: s
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_CreepyMainWindow(object):
    def setupUi(self, CreepyMainWindow):
        CreepyMainWindow.setObjectName(_fromUtf8("CreepyMainWindow"))
        CreepyMainWindow.resize(1483, 719)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CreepyMainWindow.sizePolicy().hasHeightForWidth())
        CreepyMainWindow.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../creepy/include/Eye_of_Sauron_by_Blood_Solice.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        CreepyMainWindow.setWindowIcon(icon)
        CreepyMainWindow.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(CreepyMainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.centralStackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralStackedWidget.sizePolicy().hasHeightForWidth())
        self.centralStackedWidget.setSizePolicy(sizePolicy)
        self.centralStackedWidget.setAutoFillBackground(True)
        self.centralStackedWidget.setObjectName(_fromUtf8("centralStackedWidget"))
        self.mapPage = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mapPage.sizePolicy().hasHeightForWidth())
        self.mapPage.setSizePolicy(sizePolicy)
        self.mapPage.setObjectName(_fromUtf8("mapPage"))
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.mapPage)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
<<<<<<< HEAD
        self.mapWebView = QWebView(self.mapPage)
=======
        self.mapWebView = QtWebEngineWidgets.QWebEngineView(self.mapPage)
>>>>>>> gs-ai-patch-1
        self.mapWebView.setAutoFillBackground(True)
        self.mapWebView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.mapWebView.setObjectName(_fromUtf8("mapWebView"))
        self.verticalLayout_4.addWidget(self.mapWebView)
        self.centralStackedWidget.addWidget(self.mapPage)
        self.analysisPage = QtWidgets.QWidget()
        self.analysisPage.setObjectName(_fromUtf8("analysisPage"))
        self.centralStackedWidget.addWidget(self.analysisPage)
        self.verticalLayout_2.addWidget(self.centralStackedWidget)
        CreepyMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CreepyMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1483, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuCreepy = QtWidgets.QMenu(self.menubar)
        self.menuCreepy.setObjectName(_fromUtf8("menuCreepy"))
        self.menuNewProject = QtWidgets.QMenu(self.menuCreepy)
        self.menuNewProject.setObjectName(_fromUtf8("menuNewProject"))
        self.menuExport = QtWidgets.QMenu(self.menuCreepy)
        self.menuExport.setObjectName(_fromUtf8("menuExport"))
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuFilters = QtWidgets.QMenu(self.menubar)
        self.menuFilters.setObjectName(_fromUtf8("menuFilters"))
        CreepyMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(CreepyMainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        CreepyMainWindow.setStatusBar(self.statusbar)
        self.dockWLocationsList = QtWidgets.QDockWidget(CreepyMainWindow)
        self.dockWLocationsList.setMinimumSize(QtCore.QSize(250, 127))
        self.dockWLocationsList.setObjectName(_fromUtf8("dockWLocationsList"))
        self.dockWLocationsListContents = QtWidgets.QWidget()
        self.dockWLocationsListContents.setObjectName(_fromUtf8("dockWLocationsListContents"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWLocationsListContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.locationsTableView = QtWidgets.QTableView(self.dockWLocationsListContents)
        self.locationsTableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.locationsTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.locationsTableView.setObjectName(_fromUtf8("locationsTableView"))
        self.locationsTableView.verticalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.locationsTableView)
        self.dockWLocationsList.setWidget(self.dockWLocationsListContents)
        CreepyMainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWLocationsList)
        self.dockWProjects = QtWidgets.QDockWidget(CreepyMainWindow)
        self.dockWProjects.setMinimumSize(QtCore.QSize(200, 300))
        self.dockWProjects.setStyleSheet(_fromUtf8(""))
        self.dockWProjects.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.dockWProjects.setObjectName(_fromUtf8("dockWProjects"))
        self.dockWProjectsContents = QtWidgets.QWidget()
        self.dockWProjectsContents.setObjectName(_fromUtf8("dockWProjectsContents"))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWProjectsContents)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.treeViewProjects = QtWidgets.QTreeView(self.dockWProjectsContents)
        self.treeViewProjects.setObjectName(_fromUtf8("treeViewProjects"))
        self.verticalLayout_3.addWidget(self.treeViewProjects)
        self.dockWProjects.setWidget(self.dockWProjectsContents)
        CreepyMainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWProjects)
        self.dockWCurrentLocationDetails = QtWidgets.QDockWidget(CreepyMainWindow)
        self.dockWCurrentLocationDetails.setObjectName(_fromUtf8("dockWCurrentLocationDetails"))
        self.dockWCurrentTargetDetailsContents = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWCurrentTargetDetailsContents.sizePolicy().hasHeightForWidth())
        self.dockWCurrentTargetDetailsContents.setSizePolicy(sizePolicy)
        self.dockWCurrentTargetDetailsContents.setObjectName(_fromUtf8("dockWCurrentTargetDetailsContents"))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.dockWCurrentTargetDetailsContents)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.currentTargetDetailsDetailsDateLabel = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsDetailsDateLabel.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsDetailsDateLabel.setSizePolicy(sizePolicy)
        self.currentTargetDetailsDetailsDateLabel.setTextFormat(QtCore.Qt.RichText)
        self.currentTargetDetailsDetailsDateLabel.setObjectName(_fromUtf8("currentTargetDetailsDetailsDateLabel"))
        self.horizontalLayout_2.addWidget(self.currentTargetDetailsDetailsDateLabel)
        self.currentTargetDetailsDateValue = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsDateValue.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsDateValue.setSizePolicy(sizePolicy)
        self.currentTargetDetailsDateValue.setText(_fromUtf8(""))
        self.currentTargetDetailsDateValue.setObjectName(_fromUtf8("currentTargetDetailsDateValue"))
        self.horizontalLayout_2.addWidget(self.currentTargetDetailsDateValue)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.currentTargetDetailsLocationLabel = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsLocationLabel.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsLocationLabel.setSizePolicy(sizePolicy)
        self.currentTargetDetailsLocationLabel.setObjectName(_fromUtf8("currentTargetDetailsLocationLabel"))
        self.horizontalLayout_3.addWidget(self.currentTargetDetailsLocationLabel)
        self.currentTargetDetailsLocationValue = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsLocationValue.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsLocationValue.setSizePolicy(sizePolicy)
        self.currentTargetDetailsLocationValue.setText(_fromUtf8(""))
        self.currentTargetDetailsLocationValue.setObjectName(_fromUtf8("currentTargetDetailsLocationValue"))
        self.horizontalLayout_3.addWidget(self.currentTargetDetailsLocationValue)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.currentTargetDetailsSourceLabel = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsSourceLabel.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsSourceLabel.setSizePolicy(sizePolicy)
        self.currentTargetDetailsSourceLabel.setObjectName(_fromUtf8("currentTargetDetailsSourceLabel"))
        self.horizontalLayout_4.addWidget(self.currentTargetDetailsSourceLabel)
        self.currentTargetDetailsSourceValue = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsSourceValue.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsSourceValue.setSizePolicy(sizePolicy)
        self.currentTargetDetailsSourceValue.setText(_fromUtf8(""))
        self.currentTargetDetailsSourceValue.setObjectName(_fromUtf8("currentTargetDetailsSourceValue"))
        self.horizontalLayout_4.addWidget(self.currentTargetDetailsSourceValue)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.currentTargetDetailsContextLabel = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsContextLabel.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsContextLabel.setSizePolicy(sizePolicy)
        self.currentTargetDetailsContextLabel.setObjectName(_fromUtf8("currentTargetDetailsContextLabel"))
        self.horizontalLayout_5.addWidget(self.currentTargetDetailsContextLabel)
        self.currentTargetDetailsContextValue = QtWidgets.QLabel(self.dockWCurrentTargetDetailsContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentTargetDetailsContextValue.sizePolicy().hasHeightForWidth())
        self.currentTargetDetailsContextValue.setSizePolicy(sizePolicy)
        self.currentTargetDetailsContextValue.setText(_fromUtf8(""))
        self.currentTargetDetailsContextValue.setTextFormat(QtCore.Qt.RichText)
        self.currentTargetDetailsContextValue.setWordWrap(True)
        self.currentTargetDetailsContextValue.setOpenExternalLinks(True)
        self.currentTargetDetailsContextValue.setObjectName(_fromUtf8("currentTargetDetailsContextValue"))
        self.horizontalLayout_5.addWidget(self.currentTargetDetailsContextValue)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.dockWCurrentLocationDetails.setWidget(self.dockWCurrentTargetDetailsContents)
        CreepyMainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWCurrentLocationDetails)
        self.mainToolbar = QtWidgets.QToolBar(CreepyMainWindow)
        self.mainToolbar.setObjectName(_fromUtf8("mainToolbar"))
        CreepyMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolbar)
        self.locationsActionsToolbar = QtWidgets.QToolBar(CreepyMainWindow)
        self.locationsActionsToolbar.setObjectName(_fromUtf8("locationsActionsToolbar"))
        CreepyMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.locationsActionsToolbar)
        self.actionExportKML = QtWidgets.QAction(CreepyMainWindow)
        self.actionExportKML.setCheckable(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/export")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExportKML.setIcon(icon1)
        self.actionExportKML.setObjectName(_fromUtf8("actionExportKML"))
        self.actionExportCSV = QtWidgets.QAction(CreepyMainWindow)
        self.actionExportCSV.setIcon(icon1)
        self.actionExportCSV.setObjectName(_fromUtf8("actionExportCSV"))
        self.actionExit = QtWidgets.QAction(CreepyMainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/cross")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon2)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionReportProblem = QtWidgets.QAction(CreepyMainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/exclamation")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionReportProblem.setIcon(icon3)
        self.actionReportProblem.setObjectName(_fromUtf8("actionReportProblem"))
        self.actionAbout = QtWidgets.QAction(CreepyMainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/creepy")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon4)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionPluginsConfiguration = QtWidgets.QAction(CreepyMainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/properties")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPluginsConfiguration.setIcon(icon5)
        self.actionPluginsConfiguration.setObjectName(_fromUtf8("actionPluginsConfiguration"))
        self.actionLocations_List = QtWidgets.QAction(CreepyMainWindow)
        self.actionLocations_List.setCheckable(True)
        self.actionLocations_List.setChecked(True)
        self.actionLocations_List.setSoftKeyRole(QtWidgets.QAction.NoSoftKey)
        self.actionLocations_List.setObjectName(_fromUtf8("actionLocations_List"))
        self.actionResult_Details = QtWidgets.QAction(CreepyMainWindow)
        self.actionResult_Details.setCheckable(True)
        self.actionResult_Details.setChecked(True)
        self.actionResult_Details.setObjectName(_fromUtf8("actionResult_Details"))
        self.actionAvailable_Plugins = QtWidgets.QAction(CreepyMainWindow)
        self.actionAvailable_Plugins.setCheckable(True)
        self.actionAvailable_Plugins.setChecked(True)
        self.actionAvailable_Plugins.setObjectName(_fromUtf8("actionAvailable_Plugins"))
        self.actionSettings = QtWidgets.QAction(CreepyMainWindow)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionNewPersonProject = QtWidgets.QAction(CreepyMainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/user")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewPersonProject.setIcon(icon6)
        self.actionNewPersonProject.setObjectName(_fromUtf8("actionNewPersonProject"))
        self.actionNewLocationBasedProject = QtWidgets.QAction(CreepyMainWindow)
        self.actionNewLocationBasedProject.setObjectName(_fromUtf8("actionNewLocationBasedProject"))
        self.actionAnalyzeCurrentProject = QtWidgets.QAction(CreepyMainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/target")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAnalyzeCurrentProject.setIcon(icon7)
        self.actionAnalyzeCurrentProject.setObjectName(_fromUtf8("actionAnalyzeCurrentProject"))
        self.actionDrawCurrentProject = QtWidgets.QAction(CreepyMainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/map")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDrawCurrentProject.setIcon(icon8)
        self.actionDrawCurrentProject.setObjectName(_fromUtf8("actionDrawCurrentProject"))
        self.actionFilterLocationsDate = QtWidgets.QAction(CreepyMainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/calendar")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFilterLocationsDate.setIcon(icon9)
        self.actionFilterLocationsDate.setObjectName(_fromUtf8("actionFilterLocationsDate"))
        self.actionFilterLocationsPosition = QtWidgets.QAction(CreepyMainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/marker")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFilterLocationsPosition.setIcon(icon10)
        self.actionFilterLocationsPosition.setObjectName(_fromUtf8("actionFilterLocationsPosition"))
        self.actionRemoveFilters = QtWidgets.QAction(CreepyMainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/minus")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRemoveFilters.setIcon(icon11)
        self.actionRemoveFilters.setObjectName(_fromUtf8("actionRemoveFilters"))
        self.actionShowHeatMap = QtWidgets.QAction(CreepyMainWindow)
        self.actionShowHeatMap.setCheckable(True)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/heatmap")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowHeatMap.setIcon(icon12)
        self.actionShowHeatMap.setObjectName(_fromUtf8("actionShowHeatMap"))
        self.actionLocation_Actions = QtWidgets.QAction(CreepyMainWindow)
        self.actionLocation_Actions.setObjectName(_fromUtf8("actionLocation_Actions"))
        self.actionMain_Toolbar = QtWidgets.QAction(CreepyMainWindow)
        self.actionMain_Toolbar.setObjectName(_fromUtf8("actionMain_Toolbar"))
        self.actionDeleteCurrentProject = QtWidgets.QAction(CreepyMainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/minus-circle")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDeleteCurrentProject.setIcon(icon13)
        self.actionDeleteCurrentProject.setObjectName(_fromUtf8("actionDeleteCurrentProject"))
        self.actionExportFilteredKML = QtWidgets.QAction(CreepyMainWindow)
        self.actionExportFilteredKML.setIcon(icon1)
        self.actionExportFilteredKML.setObjectName(_fromUtf8("actionExportFilteredKML"))
        self.actionExportFilteredCSV = QtWidgets.QAction(CreepyMainWindow)
        self.actionExportFilteredCSV.setIcon(icon1)
        self.actionExportFilteredCSV.setObjectName(_fromUtf8("actionExportFilteredCSV"))
        self.actionReanalyzeCurrentProject = QtWidgets.QAction(CreepyMainWindow)
        self.actionReanalyzeCurrentProject.setIcon(icon7)
        self.actionReanalyzeCurrentProject.setObjectName(_fromUtf8("actionReanalyzeCurrentProject"))
        self.actionCheckUpdates = QtWidgets.QAction(CreepyMainWindow)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/info")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCheckUpdates.setIcon(icon14)
        self.actionCheckUpdates.setObjectName(_fromUtf8("actionCheckUpdates"))
        self.menuNewProject.addAction(self.actionNewPersonProject)
        self.menuExport.addAction(self.actionExportKML)
        self.menuExport.addAction(self.actionExportCSV)
        self.menuExport.addAction(self.actionExportFilteredKML)
        self.menuExport.addAction(self.actionExportFilteredCSV)
        self.menuCreepy.addAction(self.menuNewProject.menuAction())
        self.menuCreepy.addAction(self.menuExport.menuAction())
        self.menuCreepy.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionPluginsConfiguration)
        self.menuAbout.addAction(self.actionReportProblem)
        self.menuAbout.addAction(self.actionAbout)
        self.menuAbout.addAction(self.actionCheckUpdates)
        self.menuView.addSeparator()
        self.menuFilters.addAction(self.actionFilterLocationsDate)
        self.menuFilters.addAction(self.actionFilterLocationsPosition)
        self.menuFilters.addAction(self.actionRemoveFilters)
        self.menubar.addAction(self.menuCreepy.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuFilters.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.mainToolbar.addAction(self.actionNewPersonProject)
        self.mainToolbar.addAction(self.actionPluginsConfiguration)
        self.mainToolbar.addAction(self.actionAnalyzeCurrentProject)
        self.mainToolbar.addAction(self.actionDrawCurrentProject)
        self.mainToolbar.addAction(self.actionExportKML)
        self.mainToolbar.addAction(self.actionExportCSV)
        self.mainToolbar.addSeparator()
        self.locationsActionsToolbar.addAction(self.actionFilterLocationsDate)
        self.locationsActionsToolbar.addAction(self.actionFilterLocationsPosition)
        self.locationsActionsToolbar.addAction(self.actionShowHeatMap)
        self.locationsActionsToolbar.addAction(self.actionRemoveFilters)

        self.retranslateUi(CreepyMainWindow)
        self.centralStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(CreepyMainWindow)

    def retranslateUi(self, CreepyMainWindow):
        CreepyMainWindow.setWindowTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "cree.py - Geolocation OSINT tool", None))
        self.menuCreepy.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Creepy", None))
        self.menuNewProject.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "New Project", None))
        self.menuExport.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Export", None))
        self.menuEdit.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Edit", None))
        self.menuAbout.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Help", None))
        self.menuView.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "View", None))
        self.menuFilters.setTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Filters", None))
        self.dockWLocationsList.setWindowTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Locations List", None))
        self.dockWProjects.setWindowTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Target Projects", None))
        self.dockWCurrentLocationDetails.setWindowTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "Current Location Details", None))
        self.currentTargetDetailsDetailsDateLabel.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "<b>Date:       </b>        ", None))
        self.currentTargetDetailsLocationLabel.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "<b>Location: </b>", None))
        self.currentTargetDetailsSourceLabel.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "<b>From:       <b>", None))
        self.currentTargetDetailsContextLabel.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "<b>Context:  <b>", None))
        self.mainToolbar.setWindowTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "toolBar", None))
        self.locationsActionsToolbar.setWindowTitle(QtWidgets.QApplication.translate("CreepyMainWindow", "toolBar_2", None))
        self.actionExportKML.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Export Project Locations as KML", None))
        self.actionExportKML.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Export project locations in KML format", None))
        self.actionExportCSV.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Export Project Locations as CSV", None))
        self.actionExportCSV.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Export project locations in CSV format", None))
        self.actionExit.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Exit", None))
        self.actionReportProblem.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Report a problem / bug", None))
        self.actionAbout.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "About", None))
        self.actionPluginsConfiguration.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Plugins Configuration", None))
        self.actionLocations_List.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Locations List", None))
        self.actionResult_Details.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Result Details", None))
        self.actionAvailable_Plugins.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Available Plugins", None))
        self.actionSettings.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Settings", None))
        self.actionNewPersonProject.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Person Based Project", None))
        self.actionNewLocationBasedProject.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Location Based Project", None))
        self.actionAnalyzeCurrentProject.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Analyze Current Project", None))
        self.actionAnalyzeCurrentProject.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Analyze Current Project", None))
        self.actionDrawCurrentProject.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Draw Locations for Current Project", None))
        self.actionDrawCurrentProject.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Draw Locations for the currently selected project", None))
        self.actionFilterLocationsDate.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Filter Locations by Date", None))
        self.actionFilterLocationsDate.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "<html><head/><body><p>You can filter the retrieved locations from a project based on a date range within which they have been created</p></body></html>", None))
        self.actionFilterLocationsPosition.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Filter Locations by Position", None))
        self.actionFilterLocationsPosition.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "<html><head/><body><p>You can filter the retrieved locations based on their distance from a given point in the map</p></body></html>", None))
        self.actionRemoveFilters.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Remove Filters", None))
        self.actionRemoveFilters.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "<html><head/><body><p>Remove all the filters on date and locations and show all the retreived locations on the map</p></body></html>", None))
        self.actionShowHeatMap.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Show HeatMap", None))
        self.actionShowHeatMap.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "<html><head/><body><p>Show a heatmap with the selected locations instead of pointers.</p></body></html>", None))
        self.actionLocation_Actions.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Location Actions", None))
        self.actionMain_Toolbar.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Main Toolbar", None))
        self.actionDeleteCurrentProject.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Delete Current Project", None))
        self.actionDeleteCurrentProject.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Delete this project", None))
        self.actionExportFilteredKML.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Export Filtered Locations as KML", None))
        self.actionExportFilteredKML.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Export  currently visible locations as a KML file", None))
        self.actionExportFilteredCSV.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Export Filtered Locations as CSV", None))
        self.actionExportFilteredCSV.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Export currently visible locations as CSV", None))
        self.actionReanalyzeCurrentProject.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Reanalyze Current Project", None))
        self.actionReanalyzeCurrentProject.setToolTip(QtWidgets.QApplication.translate("CreepyMainWindow", "Reanalyze Current Project", None))
        self.actionCheckUpdates.setText(QtWidgets.QApplication.translate("CreepyMainWindow", "Check for updates", None))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CreepyMainWindow = QtWidgets.QMainWindow()
    ui = Ui_CreepyMainWindow()
    ui.setupUi(CreepyMainWindow)
    CreepyMainWindow.show()
    sys.exit(app.exec_())

