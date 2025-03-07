# Note: This file was moved from components/PluginErrorsDialog.py to ui/

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
                            QFileDialog, QMessageBox, QComboBox, QLineEdit)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QBrush, QColor
from PyQt5.QtCore import Qt, QSize
from utilities.error_handling import ErrorTracker

# Setup logging
logger = logging.getLogger(__name__)

class PluginErrorsDialog(QDialog):
    """Dialog to show plugin errors and status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_tracker = ErrorTracker()
        self.setWindowTitle("Plugin Status and Errors")
        self.resize(900, 600)
        self.setupUi()
        
    def setupUi(self):
        """Set up the UI components"""
        layout = QVBoxLayout()
        
        # Header with icon
        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(":/creepy/warning").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_label)
        
        header_label = QLabel("<h2>Plugin Status and Error Report</h2>")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Statistics
        stats_layout = QHBoxLayout()
        total_errors = self.error_tracker.error_count
        unique_errors = len(self.error_tracker.errors)
        
        stats_layout.addWidget(QLabel(f"<b>Total errors:</b> {total_errors}"))
        stats_layout.addWidget(QLabel(f"<b>Unique errors:</b> {unique_errors}"))
        stats_layout.addStretch()
        
        # Add filter
        stats_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Errors", "Last 24 Hours", "Critical Only", "By Plugin"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        stats_layout.addWidget(self.filter_combo)
        
        self.plugin_filter = QComboBox()
        self.plugin_filter.setVisible(False)
        stats_layout.addWidget(self.plugin_filter)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search errors...")
        self.search_edit.textChanged.connect(self.filter_errors)
        stats_layout.addWidget(self.search_edit)
        
        layout.addLayout(stats_layout)
        
        # Errors table
        self.errors_table = QTableWidget()
        self.errors_table.setColumnCount(5)
        self.errors_table.setHorizontalHeaderLabels(["Plugin", "Error Type", "Message", "Count", "Last Seen"])
        self.errors_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.errors_table.setAlternatingRowColors(True)
        self.errors_table.setSortingEnabled(True)
        self.populate_errors_table()
        layout.addWidget(self.errors_table)
        
        # Error details
        details_layout = QHBoxLayout()
        details_label = QLabel("<b>Error Details:</b>")
        details_layout.addWidget(details_label)
        
        # Add copy button
        copy_button = QPushButton(QIcon(":/creepy/copy"), "Copy")
        copy_button.clicked.connect(self.copy_details)
        details_layout.addWidget(copy_button)
        details_layout.addStretch()
        layout.addLayout(details_layout)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        # Connect selection changed to update details
        self.errors_table.itemSelectionChanged.connect(self.selection_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Refresh button
        refresh_button = QPushButton(QIcon(":/creepy/refresh"), "Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_button)
        
        export_button = QPushButton(QIcon(":/creepy/save"), "Export Report")
        export_button.clicked.connect(self.export_report)
        button_layout.addWidget(export_button)
        
        clear_button = QPushButton(QIcon(":/creepy/trash"), "Clear Errors")
        clear_button.clicked.connect(self.clear_errors)
        button_layout.addWidget(clear_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def populate_errors_table(self):
        """Fill the table with error data"""
        self.errors_table.setRowCount(len(self.error_tracker.errors))
        
        for row, (error_key, error_data) in enumerate(sorted(
                self.error_tracker.errors.items(), 
                key=lambda x: x[1]['count'], 
                reverse=True)):
            
            # Plugin
            plugin_item = QTableWidgetItem(error_data.get('plugin', 'Unknown'))
            self.errors_table.setItem(row, 0, plugin_item)
            
            # Error type
            type_item = QTableWidgetItem(error_data['type'])
            self.errors_table.setItem(row, 1, type_item)
            
            # Message
            message_item = QTableWidgetItem(error_data['message'])
            self.errors_table.setItem(row, 2, message_item)
            
            # Count
            count_item = QTableWidgetItem(str(error_data['count']))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.errors_table.setItem(row, 3, count_item)
            
            # Last seen
            last_seen_item = QTableWidgetItem(error_data['last_seen'])
            self.errors_table.setItem(row, 4, last_seen_item)
            
        self.errors_table.sortItems(3, Qt.DescendingOrder)
        self.errors_table.resizeColumnsToContents()
        
    def selection_changed(self):
        """Update details when selection changes"""
        selected_rows = self.errors_table.selectedItems()
        if not selected_rows:
            self.details_text.clear()
            return
            
        row = selected_rows[0].row()
        error_type = self.errors_table.item(row, 1).text()
        error_message = self.errors_table.item(row, 2).text()
        
        # Find the error data
        error_key = f"{error_type}_{error_message}"
        error_data = None
        for key, data in self.error_tracker.errors.items():
            if key.startswith(error_key):
                error_data = data
                break
                
        if error_data:
            details = f"<b>Type:</b> {error_data['type']}<br>"
            details += f"<b>Message:</b> {error_data['message']}<br>"
            details += f"<b>First seen:</b> {error_data['first_seen']}<br>"
            details += f"<b>Last seen:</b> {error_data['last_seen']}<br>"
            details += f"<b>Count:</b> {error_data['count']}<br><br>"
            
            if error_data['contexts']:
                details += "<b>Contexts:</b><br>"
                for ctx in error_data['contexts']:
                    details += f"- {ctx}<br>"
                    
            self.details_text.setHtml(details)
        else:
            self.details_text.clear()
            
    def export_report(self):
        """Export error report to file"""
        self.error_tracker.save_error_report()
        report_path = os.path.join(os.getcwd(), 'creepy_error_report.json')
        
        # Ask user if they want to save to a different location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Error Report", report_path, "JSON Files (*.json)")
        
        if file_path:
            try:
                self.error_tracker.save_error_report(file_path)
                QMessageBox.information(self, "Report Exported", 
                                        f"Error report has been saved to: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", 
                                   f"Failed to export report: {str(e)}")
        
    def clear_errors(self):
        """Clear all tracked errors"""
        confirm = QMessageBox.question(
            self, "Confirm Clear", 
            "Are you sure you want to clear all error tracking data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.error_tracker.clear()
            self.populate_errors_table()
            self.details_text.clear()
            QMessageBox.information(self, "Errors Cleared", 
                                   "All tracked errors have been cleared.")
        
    def apply_filter(self):
        """Apply selected filter to the errors table"""
        filter_text = self.filter_combo.currentText()
        if filter_text == "All Errors":
            self.populate_errors_table()
        elif filter_text == "Last 24 Hours":
            self.filter_last_24_hours()
        elif filter_text == "Critical Only":
            self.filter_critical_errors()
        elif filter_text == "By Plugin":
            self.plugin_filter.setVisible(True)
            self.populate_plugin_filter()
        
    def filter_last_24_hours(self):
        """Filter errors to show only those from the last 24 hours"""
        now = datetime.now()
        filtered_errors = {k: v for k, v in self.error_tracker.errors.items() 
                           if (now - datetime.strptime(v['last_seen'], "%Y-%m-%d %H:%M:%S")).days < 1}
        self.populate_errors_table(filtered_errors)
        
    def filter_critical_errors(self):
        """Filter errors to show only critical ones"""
        filtered_errors = {k: v for k, v in self.error_tracker.errors.items() 
                           if v['type'] == 'Critical'}
        self.populate_errors_table(filtered_errors)
        
    def populate_plugin_filter(self):
        """Populate the plugin filter combo box"""
        plugins = set(error_data.get('plugin', 'Unknown') for error_data in self.error_tracker.errors.values())
        self.plugin_filter.clear()
        self.plugin_filter.addItems(sorted(plugins))
        self.plugin_filter.currentIndexChanged.connect(self.filter_by_plugin)
        
    def filter_by_plugin(self):
        """Filter errors by selected plugin"""
        selected_plugin = self.plugin_filter.currentText()
        filtered_errors = {k: v for k, v in self.error_tracker.errors.items() 
                           if v.get('plugin', 'Unknown') == selected_plugin}
        self.populate_errors_table(filtered_errors)
        
    def filter_errors(self):
        """Filter errors based on search text"""
        search_text = self.search_edit.text().lower()
        filtered_errors = {k: v for k, v in self.error_tracker.errors.items() 
                           if search_text in v['message'].lower()}
        self.populate_errors_table(filtered_errors)
        
    def refresh_data(self):
        """Refresh error data"""
        self.error_tracker.refresh()
        self.populate_errors_table()
        self.details_text.clear()
        
    def copy_details(self):
        """Copy error details to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.details_text.toPlainText())
        QMessageBox.information(self, "Copied", "Error details copied to clipboard.")