#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QCheckBox, QComboBox, QGroupBox, QSlider, QSpinBox,
                            QColorDialog, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QColor

class MapOptionsDialog(QDialog):
    """Dialog for configuring map display options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Display Options")
        self.resize(450, 500)
        self.settings = QSettings("CreepyAI", "Creepy")
        self.setupUi()
        self.loadSettings()
        
    def setupUi(self):
        """Set up the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Map type group
        map_type_group = QGroupBox("Map Type")
        map_type_layout = QVBoxLayout()
        
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems(["Roadmap", "Satellite", "Hybrid", "Terrain"])
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
        
        self.marker_opacity_slider = QSlider(Qt.Horizontal)
        self.marker_opacity_slider.setRange(1, 10)
        self.marker_opacity_slider.setValue(8)
        marker_layout.addRow("Marker Opacity:", self.marker_opacity_slider)
        
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
        self.map_type_combo.setCurrentText(self.settings.value("map/type", "Roadmap"))
        self.marker_size_spin.setValue(int(self.settings.value("map/marker_size", 10)))
        self.marker_opacity_slider.setValue(int(self.settings.value("map/marker_opacity", 8)))
        self.cluster_markers_check.setChecked(self.settings.value("map/cluster_markers", True, type=bool))
        self.show_labels_check.setChecked(self.settings.value("map/show_labels", True, type=bool))
        self.heatmap_radius_spin.setValue(int(self.settings.value("map/heatmap_radius", 30)))
        self.heatmap_intensity_slider.setValue(int(self.settings.value("map/heatmap_intensity", 5)))
        self.show_timeline_check.setChecked(self.settings.value("map/show_timeline", True, type=bool))
        self.animate_movement_check.setChecked(self.settings.value("map/animate_movement", False, type=bool))
        self.show_photos_check.setChecked(self.settings.value("map/show_photos", True, type=bool))
        
        # Load colors
        start_color = self.settings.value("map/heatmap_start_color", "rgba(0, 255, 0, 0.7)")
        end_color = self.settings.value("map/heatmap_end_color", "rgba(255, 0, 0, 0.7)")
        self.gradient_start_button.setStyleSheet(f"background-color: {start_color};")
        self.gradient_end_button.setStyleSheet(f"background-color: {end_color};")
        
    def saveSettings(self):
        """Save settings to QSettings"""
        self.settings.setValue("map/type", self.map_type_combo.currentText())
        self.settings.setValue("map/marker_size", self.marker_size_spin.value())
        self.settings.setValue("map/marker_opacity", self.marker_opacity_slider.value())
        self.settings.setValue("map/cluster_markers", self.cluster_markers_check.isChecked())
        self.settings.setValue("map/show_labels", self.show_labels_check.isChecked())
        self.settings.setValue("map/heatmap_radius", self.heatmap_radius_spin.value())
        self.settings.setValue("map/heatmap_intensity", self.heatmap_intensity_slider.value())
        self.settings.setValue("map/show_timeline", self.show_timeline_check.isChecked())
        self.settings.setValue("map/animate_movement", self.animate_movement_check.isChecked())
        self.settings.setValue("map/show_photos", self.show_photos_check.isChecked())
        
        # Save colors - extract from stylesheet
        start_color = self.gradient_start_button.styleSheet().split(":")[-1].strip().rstrip(";")
        end_color = self.gradient_end_button.styleSheet().split(":")[-1].strip().rstrip(";")
        self.settings.setValue("map/heatmap_start_color", start_color)
        self.settings.setValue("map/heatmap_end_color", end_color)
    
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
