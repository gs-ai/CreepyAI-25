"""
Location Detail Dialog for CreepyAI
Shows detailed information about a selected location
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QSizePolicy, QTabWidget,
    QTextEdit, QDialogButtonBox, QApplication, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont

from app.plugins.base_plugin import LocationPoint
from app.core.include.button_styles import ButtonStyles  # Import ButtonStyles

logger = logging.getLogger(__name__)

class LocationDetailDialog(QDialog):
    """Dialog to display detailed information about a location point"""
    
    def __init__(self, location_point: LocationPoint, parent=None):
        super().__init__(parent)
        self.location_point = location_point
        self.setWindowTitle(f"Location Details - {location_point.source}")
        self.resize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header with source icon and title
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Try to get icon for the source
        icon_path = os.path.join("app", "resources", "icons", f"{self.location_point.source.lower().split()[0]}-icon.png")
        icon_label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("📍")
            icon_label.setFont(QFont("Arial", 24))
        
        icon_label.setFixedSize(QSize(40, 40))
        header_layout.addWidget(icon_label)
        
        # Title and timestamp
        title_layout = QVBoxLayout()
        title = QLabel(self.location_point.source)
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: #333;")
        
        timestamp = QLabel(self.location_point.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        timestamp.setStyleSheet("font-size: 14px; color: #666;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(timestamp)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Tabs for different views
        tab_widget = QTabWidget()
        
        # Details tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)
        
        # Coordinates
        grid_layout.addWidget(QLabel("<b>Latitude:</b>"), 0, 0)
        grid_layout.addWidget(QLabel(f"{self.location_point.latitude:.6f}"), 0, 1)
        
        grid_layout.addWidget(QLabel("<b>Longitude:</b>"), 1, 0)
        grid_layout.addWidget(QLabel(f"{self.location_point.longitude:.6f}"), 1, 1)
        
        grid_layout.addWidget(QLabel("<b>Source:</b>"), 2, 0)
        grid_layout.addWidget(QLabel(self.location_point.source), 2, 1)
        
        grid_layout.addWidget(QLabel("<b>Timestamp:</b>"), 3, 0)
        grid_layout.addWidget(QLabel(self.location_point.timestamp.strftime("%Y-%m-%d %H:%M:%S")), 3, 1)
        
        details_layout.addLayout(grid_layout)
        
        # Context section
        details_layout.addWidget(QLabel("<b>Context:</b>"))
        context_text = QTextEdit()
        context_text.setReadOnly(True)
        context_text.setText(self.location_point.context)
        context_text.setMinimumHeight(100)
        details_layout.addWidget(context_text)
        
        # Address lookup
        address_frame = QFrame()
        address_frame.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        address_layout = QVBoxLayout(address_frame)
        
        address_layout.addWidget(QLabel("<b>Reverse Geocoding:</b>"))
        
        self.address_label = QLabel("Loading address information...")
        address_layout.addWidget(self.address_label)
        
        # Enhance lookup button with primary style
        lookup_button = QPushButton("Lookup Address")
        lookup_button.setIcon(QIcon(os.path.join("app", "resources", "icons", "map-marker-icon.png")))
        lookup_button.setToolTip("Lookup address for these coordinates")
        ButtonStyles.primary_button(lookup_button)  # Apply primary style
        lookup_button.clicked.connect(self.lookup_address)
        address_layout.addWidget(lookup_button)
        
        details_layout.addWidget(address_frame)
        details_layout.addStretch()
        
        tab_widget.addTab(details_widget, "Details")
        
        # Map tab (placeholder for future implementation)
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        map_layout.addWidget(QLabel("Map view will be added in a future update."))
        
        tab_widget.addTab(map_widget, "Map")
        
        layout.addWidget(tab_widget)
        
        # Button box with enhanced styling
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_button = button_box.button(QDialogButtonBox.Close)
        ButtonStyles.secondary_button(close_button)  # Apply secondary style
        close_button.setText("Close")
        close_button.setIcon(QIcon(os.path.join("app", "resources", "icons", "close-icon.png")))
        
        # Add more actions
        copy_coords_btn = QPushButton("Copy Coordinates")
        copy_coords_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "copy-icon.png")))
        copy_coords_btn.clicked.connect(self.copy_coordinates)
        ButtonStyles.secondary_button(copy_coords_btn)  # Apply secondary style
        button_box.addButton(copy_coords_btn, QDialogButtonBox.ActionRole)
        
        export_btn = QPushButton("Export")
        export_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "export-icon.png")))
        export_btn.clicked.connect(self.export_location)
        ButtonStyles.secondary_button(export_btn)  # Apply secondary style
        button_box.addButton(export_btn, QDialogButtonBox.ActionRole)
        
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Perform address lookup automatically
        self.lookup_address()
    
    def lookup_address(self):
        """Look up address for the coordinates"""
        try:
            from app.plugins.geocoding_helper import GeocodingHelper
            geocoder = GeocodingHelper()
            
            address = geocoder.reverse_geocode(
                self.location_point.latitude,
                self.location_point.longitude
            )
            
            if address:
                self.address_label.setText(address)
            else:
                self.address_label.setText("Address lookup failed.")
        except Exception as e:
            logger.error(f"Error looking up address: {e}")
            self.address_label.setText("Error looking up address.")
    
    def copy_coordinates(self):
        """Copy coordinates to clipboard"""
        coords_text = f"{self.location_point.latitude:.6f}, {self.location_point.longitude:.6f}"
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(coords_text)
        
        # Show feedback
        self.statusBar().showMessage("Coordinates copied to clipboard", 2000)
    
    def export_location(self):
        """Export location data to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Location", "", "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.json'):
                # Export as JSON
                import json
                location_data = {
                    'latitude': self.location_point.latitude,
                    'longitude': self.location_point.longitude,
                    'timestamp': self.location_point.timestamp.isoformat(),
                    'source': self.location_point.source,
                    'context': self.location_point.context
                }
                
                with open(filename, 'w') as f:
                    json.dump(location_data, f, indent=2)
                    
            elif filename.endswith('.csv'):
                # Export as CSV
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['latitude', 'longitude', 'timestamp', 'source', 'context'])
                    writer.writerow([
                        self.location_point.latitude,
                        self.location_point.longitude,
                        self.location_point.timestamp.isoformat(),
                        self.location_point.source,
                        self.location_point.context
                    ])
            else:
                # Default to text format
                with open(filename, 'w') as f:
                    f.write(f"Latitude: {self.location_point.latitude}\n")
                    f.write(f"Longitude: {self.location_point.longitude}\n")
                    f.write(f"Timestamp: {self.location_point.timestamp}\n")
                    f.write(f"Source: {self.location_point.source}\n")
                    f.write(f"Context: {self.location_point.context}\n")
            
            QMessageBox.information(self, "Export Successful", f"Location exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export location: {str(e)}")
