#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateTimeEdit, QCheckBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QDateTime

logger = logging.getLogger(__name__)

class FilterLocationsDateDialog(QDialog):
    """Dialog for filtering locations by date range."""
    
    def __init__(self, project, parent=None):
        super(FilterLocationsDateDialog, self).__init__(parent)
        
        self.setWindowTitle("Filter Locations by Date")
        self.setFixedWidth(400)
        
        self.project = project
        
        # Get date range from locations
        self.start_date, self.end_date = self._get_date_range()
        
        # Create layout
        layout = QVBoxLayout()
        
        # Information label
        info_label = QLabel(
            "Filter locations based on their timestamp. "
            "Only locations within the selected date range will be displayed."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Date range group
        date_group = QGroupBox("Date Range")
        date_form = QFormLayout()
        
        # Start date controls
        start_layout = QHBoxLayout()
        self.start_check = QCheckBox("Enable")
        self.start_check.setChecked(True)
        self.start_check.stateChanged.connect(self._update_controls)
        start_layout.addWidget(self.start_check)
        
        self.start_edit = QDateTimeEdit()
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDateTime(self.start_date)
        start_layout.addWidget(self.start_edit)
        
        date_form.addRow("From:", start_layout)
        
        # End date controls
        end_layout = QHBoxLayout()
        self.end_check = QCheckBox("Enable")
        self.end_check.setChecked(True)
        self.end_check.stateChanged.connect(self._update_controls)
        end_layout.addWidget(self.end_check)
        
        self.end_edit = QDateTimeEdit()
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDateTime(self.end_date)
        end_layout.addWidget(self.end_edit)
        
        date_form.addRow("To:", end_layout)
        
        date_group.setLayout(date_form)
        layout.addWidget(date_group)
        
        # Stats label - show how many locations are in the full range
        self.stats_label = QLabel()
        self._update_stats_label()
        layout.addWidget(self.stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply Filter")
        self.apply_button.clicked.connect(self.apply_filter)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Update UI state
        self._update_controls()
    
    def _get_date_range(self):
        """Get the date range from the project's locations."""
        start_date = QDateTime.currentDateTime().addDays(-30)  # Default to last 30 days
        end_date = QDateTime.currentDateTime()
        
        if self.project and hasattr(self.project, 'locations'):
            min_date, max_date = self.project.locations.get_date_range()
            
            if min_date:
                start_date = QDateTime(min_date)
            if max_date:
                end_date = QDateTime(max_date)
        
        return start_date, end_date
    
    def _update_controls(self):
        """Update the enabled state of date controls."""
        self.start_edit.setEnabled(self.start_check.isChecked())
        self.end_edit.setEnabled(self.end_check.isChecked())
    
    def _update_stats_label(self):
        """Update the stats label with location counts."""
        if not self.project or not hasattr(self.project, 'locations'):
            self.stats_label.setText("No locations available")
            return
            
        total_count = self.project.locations.count()
        self.stats_label.setText(f"Total locations in project: {total_count}")
    
    def apply_filter(self):
        """Apply the date filter to the project's locations."""
        if not self.project or not hasattr(self.project, 'locations'):
            self.reject()
            return
            
        # Get filter parameters
        start_date = self.start_edit.dateTime().toPyDateTime() if self.start_check.isChecked() else None
        end_date = self.end_edit.dateTime().toPyDateTime() if self.end_check.isChecked() else None
        
        # Apply filter
        try:
            filtered_count = self.project.locations.filter_by_date(start_date, end_date)
            logger.info(f"Applied date filter: {filtered_count} locations match")
            self.accept()
        except Exception as e:
            logger.error(f"Error applying date filter: {str(e)}")
            self.reject()