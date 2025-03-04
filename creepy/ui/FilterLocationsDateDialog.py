<<<<<<< HEAD
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
=======
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\filterLocationsDateDialog.ui'
#
# Created: Fri Jan 31 15:33:14 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FilterLocationsDateDialog(object):
    def setupUi(self, FilterLocationsDateDialog):
        FilterLocationsDateDialog.setObjectName(_fromUtf8("FilterLocationsDateDialog"))
        FilterLocationsDateDialog.resize(575, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/calendar")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FilterLocationsDateDialog.setWindowIcon(icon)
        FilterLocationsDateDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterLocationsDateDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.containerLayout = QtWidgets.QVBoxLayout()
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtWidgets.QLabel(FilterLocationsDateDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.calendarContainerLayout = QtWidgets.QHBoxLayout()
        self.calendarContainerLayout.setObjectName(_fromUtf8("calendarContainerLayout"))
        self.startDateContainer = QtWidgets.QVBoxLayout()
        self.startDateContainer.setObjectName(_fromUtf8("startDateContainer"))
        self.startDateLabel = QtWidgets.QLabel(FilterLocationsDateDialog)
        self.startDateLabel.setTextFormat(QtCore.Qt.AutoText)
        self.startDateLabel.setObjectName(_fromUtf8("startDateLabel"))
        self.startDateContainer.addWidget(self.startDateLabel)
        self.stardateCalendarWidget = QtWidgets.QCalendarWidget(FilterLocationsDateDialog)
        self.stardateCalendarWidget.setObjectName(_fromUtf8("stardateCalendarWidget"))
        self.startDateContainer.addWidget(self.stardateCalendarWidget)
        self.calendarContainerLayout.addLayout(self.startDateContainer)
        self.endDateContainer = QtWidgets.QVBoxLayout()
        self.endDateContainer.setObjectName(_fromUtf8("endDateContainer"))
        self.endDateLabel = QtWidgets.QLabel(FilterLocationsDateDialog)
        self.endDateLabel.setObjectName(_fromUtf8("endDateLabel"))
        self.endDateContainer.addWidget(self.endDateLabel)
        self.endDateCalendarWidget = QtWidgets.QCalendarWidget(FilterLocationsDateDialog)
        self.endDateCalendarWidget.setObjectName(_fromUtf8("endDateCalendarWidget"))
        self.endDateContainer.addWidget(self.endDateCalendarWidget)
        self.calendarContainerLayout.addLayout(self.endDateContainer)
        self.containerLayout.addLayout(self.calendarContainerLayout)
        self.timeContainerLayout = QtWidgets.QHBoxLayout()
        self.timeContainerLayout.setObjectName(_fromUtf8("timeContainerLayout"))
        self.startDateTimeEdit = QtWidgets.QTimeEdit(FilterLocationsDateDialog)
        self.startDateTimeEdit.setObjectName(_fromUtf8("startDateTimeEdit"))
        self.timeContainerLayout.addWidget(self.startDateTimeEdit)
        self.endDateTimeEdit = QtWidgets.QTimeEdit(FilterLocationsDateDialog)
        self.endDateTimeEdit.setObjectName(_fromUtf8("endDateTimeEdit"))
        self.timeContainerLayout.addWidget(self.endDateTimeEdit)
        self.containerLayout.addLayout(self.timeContainerLayout)
        self.verticalLayout.addLayout(self.containerLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(FilterLocationsDateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FilterLocationsDateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FilterLocationsDateDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FilterLocationsDateDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FilterLocationsDateDialog)

    def retranslateUi(self, FilterLocationsDateDialog):
        FilterLocationsDateDialog.setWindowTitle(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "Filter Locations By Date", None, -1))
        self.titleLabel.setText(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Select the start and end dates and times</span></p></body></html>", None, -1))
        self.startDateLabel.setText(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "<b>Start Date</b>", None, -1))
        self.endDateLabel.setText(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "<b>End Date</b>", None, -1))
        self.startDateTimeEdit.setDisplayFormat(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "hh:mm:ss AP", None, -1))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FilterLocationsDateDialog = QtWidgets.QDialog()
    ui = Ui_FilterLocationsDateDialog()
    ui.setupUi(FilterLocationsDateDialog)
    FilterLocationsDateDialog.show()
    sys.exit(app.exec_())
>>>>>>> gs-ai-patch-1
