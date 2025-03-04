#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QDate, QTime
from ui.FilterLocationsDateDialogUI import Ui_FilterLocationsDateDialog
from yapsy.PluginManager import PluginManagerSingleton

class FilterLocationsDateDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_FilterLocationsDateDialog()
        self.ui.setupUi(self)
        
        # Set up defaults
        today = QDate.currentDate()
        oneMonthAgo = today.addMonths(-1)
        
        # Set start date to one month ago by default
        self.ui.startDateCalendarWidget.setSelectedDate(oneMonthAgo)
        self.ui.endDateCalendarWidget.setSelectedDate(today)
        
        # Set time default values
        self.ui.startDateTimeEdit.setTime(QTime(0, 0, 0))
        self.ui.endDateTimeEdit.setTime(QTime(23, 59, 59))
        
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        self.setupConnections()
        self.setupPlugins()

    def setupConnections(self):
        try:
            # Add any signal-slot connections here
            pass
        except Exception as e:
            print(f"Error setting up connections: {str(e)}")

    def setupPlugins(self):
        try:
            self.PluginManager = PluginManagerSingleton.get()
            self.PluginManager.setPluginPlaces(['/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/plugins'])
            self.PluginManager.locatePlugins()
            self.PluginManager.loadPlugins()
        except Exception as e:
            print(f"Error setting up plugins: {e}")