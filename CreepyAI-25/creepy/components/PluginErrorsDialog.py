#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
                            QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from utilities.error_handling import ErrorTracker

class PluginErrorsDialog(QDialog):
    """Dialog to show plugin errors and status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_tracker = ErrorTracker()
        self.setWindowTitle("Plugin Status and Errors")
        self.resize(800, 600)
        self.setupUi()
        
    def setupUi(self):
        """Set up the UI components"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("<h2>Plugin Status and Error Report</h2>")
        layout.addWidget(header_label)
        
        # Statistics
        stats_layout = QHBoxLayout()
        total_errors = self.error_tracker.error_count
        unique_errors = len(self.error_tracker.errors)
        
        stats_layout.addWidget(QLabel(f"<b>Total errors:</b> {total_errors}"))
        stats_layout.addWidget(QLabel(f"<b>Unique errors:</b> {unique_errors}"))
        layout.addLayout(stats_layout)
        
        # Errors table
        self.errors_table = QTableWidget()
        self.errors_table.setColumnCount(4)
        self.errors_table.setHorizontalHeaderLabels(["Error Type", "Message", "Count", "Last Seen"])
        self.errors_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.populate_errors_table()
        layout.addWidget(self.errors_table)
        
        # Error details
        details_label = QLabel("<b>Error Details:</b>")
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)
        
        # Connect selection changed to update details
        self.errors_table.itemSelectionChanged.connect(self.selection_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("Export Report")
        export_button.clicked.connect(self.export_report)
        button_layout.addWidget(export_button)
        
        clear_button = QPushButton("Clear Errors")
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
            
            # Error type
            type_item = QTableWidgetItem(error_data['type'])
            self.errors_table.setItem(row, 0, type_item)
            
            # Message
            message_item = QTableWidgetItem(error_data['message'])
            self.errors_table.setItem(row, 1, message_item)
            
            # Count
            count_item = QTableWidgetItem(str(error_data['count']))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.errors_table.setItem(row, 2, count_item)
            
            # Last seen
            last_seen_item = QTableWidgetItem(error_data['last_seen'])
            self.errors_table.setItem(row, 3, last_seen_item)
            
        self.errors_table.sortItems(2, Qt.DescendingOrder)
        self.errors_table.resizeColumnsToContents()
        
    def selection_changed(self):
        """Update details when selection changes"""
        selected_rows = self.errors_table.selectedItems()
        if not selected_rows:
            self.details_text.clear()
            return
            
        row = selected_rows[0].row()
        error_type = self.errors_table.item(row, 0).text()
        error_message = self.errors_table.item(row, 1).text()
        
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