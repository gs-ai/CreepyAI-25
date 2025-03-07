#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QMessageBox
from ui.FilterLocationsDateDialog import Ui_FilterLocationsDateDialog
from PyQt5.QtCore import QDateTime, QDate

class FilterLocationsDateDialog(QDialog):
    """Dialog for filtering locations by date."""
    
    def __init__(self, parent=None, project=None):
        super(FilterLocationsDateDialog, self).__init__(parent)
        self.ui = Ui_FilterLocationsDateDialog()
        self.ui.setupUi(self)
        self.project = project
        
        # Initialize with project dates if available
        if project and hasattr(project, 'locations') and project.locations:
            min_date, max_date = None, None
            for loc in project.locations:
                if not min_date or loc.datetime < min_date:
                    min_date = loc.datetime
                if not max_date or loc.datetime > max_date:
                    max_date = loc.datetime
                    
            if min_date and max_date:
                from PyQt5.QtCore import QDate, QTime
                
                # Set start date
                start_date = QDate(min_date.year, min_date.month, min_date.day)
                start_time = QTime(min_date.hour, min_date.minute, min_date.second)
                self.ui.startDateCalendarWidget.setSelectedDate(start_date)
                self.ui.startDateTimeEdit.setTime(start_time)
                
                # Set end date
                end_date = QDate(max_date.year, max_date.month, max_date.day)
                end_time = QTime(max_date.hour, max_date.minute, max_date.second)
                self.ui.endDateCalendarWidget.setSelectedDate(end_date)
                self.ui.endDateTimeEdit.setTime(end_time)
        
        # Initialize with default values - one month range
        default_end_date = QDate.currentDate()
        default_start_date = default_end_date.addMonths(-1)
        
        self.ui.startDateCalendarWidget.setSelectedDate(default_start_date)
        self.ui.endDateCalendarWidget.setSelectedDate(default_end_date)
        
        # Restrict end date to not exceed current date
        self.ui.endDateCalendarWidget.setMaximumDate(default_end_date)
        
        # Connect signals
        self.ui.startDateCalendarWidget.clicked.connect(self.validate_dates)
        self.ui.endDateCalendarWidget.clicked.connect(self.validate_dates)
        
    def validate_dates(self):
        """Validate that start date is before end date"""
        start_date = self.ui.startDateCalendarWidget.selectedDate()
        end_date = self.ui.endDateCalendarWidget.selectedDate()
        
        if start_date > end_date:
            QMessageBox.warning(self, 
                               "Invalid Date Selection", 
                               "Start date must be before end date.\nPlease select a valid date range.")
            # Reset end date to be at least the start date
            self.ui.endDateCalendarWidget.setSelectedDate(start_date)