#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox, QFormLayout, QSlider
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class FilterLocationsPointDialog(QDialog):
    """Dialog for filtering locations by distance from a point."""
    
    def __init__(self, project, parent=None):
        super(FilterLocationsPointDialog, self).__init__(parent)
        
        self.setWindowTitle("Filter Locations by Distance")
        self.setFixedWidth(400)
        
        self.project = project
        
        # Create layout
        layout = QVBoxLayout()
        
        # Information label
        info_label = QLabel(
            "Filter locations based on their distance from a specific point. "
            "Only locations within the specified radius will be displayed."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Point group
        point_group = QGroupBox("Center Point")
        point_form = QFormLayout()
        
        # Latitude control
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setDecimals(6)
        self.lat_spin.setValue(0)
        point_form.addRow("Latitude:", self.lat_spin)
        
        # Longitude control
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setDecimals(6)
        self.lon_spin.setValue(0)
        point_form.addRow("Longitude:", self.lon_spin)
        
        point_group.setLayout(point_form)
        layout.addWidget(point_group)
        
        # Radius group
        radius_group = QGroupBox("Search Radius")
        radius_layout = QVBoxLayout()
        
        # Radius slider and value display
        slider_layout = QHBoxLayout()
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(1, 500)
        self.radius_slider.setValue(10)
        self.radius_slider.setTickInterval(50)
        self.radius_slider.setTickPosition(QSlider.TicksBelow)
        slider_layout.addWidget(self.radius_slider)
        
        self.radius_label = QLabel("10 km")
        slider_layout.addWidget(self.radius_label)
        
        radius_layout.addLayout(slider_layout)
        
        # Connect slider to label update
        self.radius_slider.valueChanged.connect(self._update_radius_label)
        
        radius_group.setLayout(radius_layout)
        layout.addWidget(radius_group)
        
        # Stats label - show how many locations are in the full dataset
        self.stats_label = QLabel()
        self._update_stats_label()
        layout.addWidget(self.stats_label)
        
        # Use current center button
        center_button = QPushButton("Use Current Map Center")
        center_button.clicked.connect(self._use_current_center)
        layout.addWidget(center_button)
        
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
        
        # Set default center point to the center of all locations
        self._set_default_center()
    
    def _set_default_center(self):
        """Set the default center point to the center of all locations."""
        if self.project and hasattr(self.project, 'locations'):
            center_lat, center_lon = self.project.locations.get_center_point()
            
            self.lat_spin.setValue(center_lat)
            self.lon_spin.setValue(center_lon)
    
    def _update_radius_label(self, value):
        """Update the radius label with the slider value."""
        self.radius_label.setText(f"{value} km")
    
    def _update_stats_label(self):
        """Update the stats label with location counts."""
        if not self.project or not hasattr(self.project, 'locations'):
            self.stats_label.setText("No locations available")
            return
            
        total_count = self.project.locations.count()
        self.stats_label.setText(f"Total locations in project: {total_count}")
    
    def _use_current_center(self):
        """Use the current map center as the filter point."""
        # This would normally get the current center from the map view
        # For now, we'll just keep the current values
        pass
    
    def apply_filter(self):
        """Apply the distance filter to the project's locations."""
        if not self.project or not hasattr(self.project, 'locations'):
            self.reject()
            return
            
        # Get filter parameters
        latitude = self.lat_spin.value()
        longitude = self.lon_spin.value()
        radius_km = self.radius_slider.value()
        
        # Apply filter
        try:
            filtered_count = self.project.locations.filter_by_distance(latitude, longitude, radius_km)
            logger.info(f"Applied distance filter: {filtered_count} locations match")
            self.accept()
        except Exception as e:
            logger.error(f"Error applying distance filter: {str(e)}")
            self.reject()

