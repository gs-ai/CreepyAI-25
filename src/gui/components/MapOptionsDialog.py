#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QCheckBox, QComboBox, QGroupBox, QFormLayout,
                           QSpinBox, QDialogButtonBox, QColorDialog, QLineEdit)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor

class MapOptionsDialog(QDialog):
    """Dialog for configuring map display options"""
    
    def __init__(self, parent=None):
        super(MapOptionsDialog, self).__init__(parent)
        
        self.setWindowTitle("Map Options")
        self.setMinimumWidth(400)
        
        # Load current settings
        self.settings = QSettings("CreepyAI", "CreepyAI")
        self.map_settings = {
            'map_type': self.settings.value('map/type', 'OpenStreetMap'),
            'cluster_points': self.settings.value('map/cluster_points', True, type=bool),
            'show_lines': self.settings.value('map/show_lines', True, type=bool),
            'line_color': self.settings.value('map/line_color', '#3388ff'),
            'line_weight': self.settings.value('map/line_weight', 3, type=int),
            'marker_size': self.settings.value('map/marker_size', 10, type=int),
            'heatmap_enabled': self.settings.value('map/heatmap_enabled', False, type=bool),
            'heatmap_radius': self.settings.value('map/heatmap_radius', 25, type=int),
            'heatmap_intensity': self.settings.value('map/heatmap_intensity', 5, type=int),
            'heatmap_gradient_start': self.settings.value('map/heatmap_gradient_start', 'rgba(0, 255, 0, 0.7)'),
            'heatmap_gradient_end': self.settings.value('map/heatmap_gradient_end', 'rgba(255, 0, 0, 0.7)')
        }
        
        self.setupUi()
        self.loadSettings()
        
    def setupUi(self):
        """Set up the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Map type group
        map_type_group = QGroupBox("Map Type")
        map_type_layout = QVBoxLayout()
        
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems(["OpenStreetMap", "Google Maps", "Bing Maps", "Mapbox"])
        map_type_layout.addWidget(self.map_type_combo)
        
        map_type_group.setLayout(map_type_layout)
        main_layout.addWidget(map_type_group)
        
        # Marker options group
        marker_group = QGroupBox("Markers")
        marker_layout = QFormLayout()
        
        self.marker_size_spin = QSpinBox()
        self.marker_size_spin.setRange(1, 20)
        self.marker_size_spin.setValue(10)
        marker_layout.addRow("Marker Size:", self.marker_size_spin)
        
        self.cluster_markers_check = QCheckBox("Cluster nearby markers")
        marker_layout.addRow(self.cluster_markers_check)
        
        self.show_labels_check = QCheckBox("Show marker labels")
        marker_layout.addRow(self.show_labels_check)
        
        marker_group.setLayout(marker_layout)
        main_layout.addWidget(marker_group)
        
        # Heatmap options group
        heatmap_group = QGroupBox("Heatmap")
        heatmap_layout = QFormLayout()
        
        self.heatmap_radius_spin = QSpinBox()
        self.heatmap_radius_spin.setRange(10, 100)
        self.heatmap_radius_spin.setValue(30)
        heatmap_layout.addRow("Heatmap Radius:", self.heatmap_radius_spin)
        
        self.heatmap_intensity_slider = QSlider(Qt.Horizontal)
        self.heatmap_intensity_slider.setRange(1, 10)
        self.heatmap_intensity_slider.setValue(5)
        heatmap_layout.addRow("Intensity:", self.heatmap_intensity_slider)
        
        # Gradient start color
        self.gradient_start_button = QPushButton()
        self.gradient_start_button.setAutoFillBackground(True)
        self.gradient_start_button.setStyleSheet("background-color: rgba(0, 255, 0, 0.7);")
        self.gradient_start_button.clicked.connect(self.choose_start_color)
        heatmap_layout.addRow("Start Color:", self.gradient_start_button)
        
        # Gradient end color
        self.gradient_end_button = QPushButton()
        self.gradient_end_button.setAutoFillBackground(True)
        self.gradient_end_button.setStyleSheet("background-color: rgba(255, 0, 0, 0.7);")
        self.gradient_end_button.clicked.connect(self.choose_end_color)
        heatmap_layout.addRow("End Color:", self.gradient_end_button)
        
        heatmap_group.setLayout(heatmap_layout)
        main_layout.addWidget(heatmap_group)
        
        # Display options
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout()
        
        self.show_timeline_check = QCheckBox("Show timeline control")
        display_layout.addWidget(self.show_timeline_check)
        
        self.animate_movement_check = QCheckBox("Animate movement between points")
        display_layout.addWidget(self.animate_movement_check)
        
        self.show_photos_check = QCheckBox("Show photo thumbnails on map")
        display_layout.addWidget(self.show_photos_check)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        main_layout.addWidget(button_box)
        
    def loadSettings(self):
        """Load settings from QSettings"""
        self.map_type_combo.setCurrentText(self.map_settings['map_type'])
        self.marker_size_spin.setValue(self.map_settings['marker_size'])
        self.cluster_markers_check.setChecked(self.map_settings['cluster_points'])
        self.show_labels_check.setChecked(self.map_settings['show_lines'])
        self.heatmap_radius_spin.setValue(self.map_settings['heatmap_radius'])
        self.heatmap_intensity_slider.setValue(self.map_settings['heatmap_intensity'])
        self.show_timeline_check.setChecked(self.map_settings['heatmap_enabled'])
        self.animate_movement_check.setChecked(self.map_settings['heatmap_enabled'])
        self.show_photos_check.setChecked(self.map_settings['heatmap_enabled'])
        
        # Load colors
        start_color = self.map_settings['heatmap_gradient_start']
        end_color = self.map_settings['heatmap_gradient_end']
        self.gradient_start_button.setStyleSheet(f"background-color: {start_color};")
        self.gradient_end_button.setStyleSheet(f"background-color: {end_color};")
        
    def saveSettings(self):
        """Save settings to QSettings"""
        self.settings.setValue("map/type", self.map_type_combo.currentText())
        self.settings.setValue("map/marker_size", self.marker_size_spin.value())
        self.settings.setValue("map/cluster_points", self.cluster_markers_check.isChecked())
        self.settings.setValue("map/show_lines", self.show_labels_check.isChecked())
        self.settings.setValue("map/heatmap_radius", self.heatmap_radius_spin.value())
        self.settings.setValue("map/heatmap_intensity", self.heatmap_intensity_slider.value())
        self.settings.setValue("map/heatmap_enabled", self.show_timeline_check.isChecked())
        self.settings.setValue("map/heatmap_enabled", self.animate_movement_check.isChecked())
        self.settings.setValue("map/heatmap_enabled", self.show_photos_check.isChecked())
        
        # Save colors - extract from stylesheet
        start_color = self.gradient_start_button.styleSheet().split(":")[-1].strip().rstrip(";")
        end_color = self.gradient_end_button.styleSheet().split(":")[-1].strip().rstrip(";")
        self.settings.setValue("map/heatmap_gradient_start", start_color)
        self.settings.setValue("map/heatmap_gradient_end", end_color)
    
    def choose_start_color(self):
        """Show color dialog for selecting gradient start color"""
        color = QColorDialog.getColor(QColor(0, 255, 0, 178), self, "Select Gradient Start Color", 
                                     QColorDialog.ShowAlphaChannel)
        if color.isValid():
            rgba = f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha() / 255.0})"
            self.gradient_start_button.setStyleSheet(f"background-color: {rgba};")
    
    def choose_end_color(self):
        """Show color dialog for selecting gradient end color"""
        color = QColorDialog.getColor(QColor(255, 0, 0, 178), self, "Select Gradient End Color", 
                                     QColorDialog.ShowAlphaChannel)
        if color.isValid():
            rgba = f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha() / 255.0})"
            self.gradient_end_button.setStyleSheet(f"background-color: {rgba};")
    
    def apply_settings(self):
        """Apply settings without closing the dialog"""
        self.saveSettings()
        
        # Emit signal that settings have changed (would be implemented in actual app)
        self.parent().updateMapOptions() if self.parent() else None
        
    def accept(self):
        """Override accept to save settings before closing"""
        self.saveSettings()
        super().accept()
