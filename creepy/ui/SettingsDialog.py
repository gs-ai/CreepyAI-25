#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QWidget, QLabel, QLineEdit, QCheckBox, QSpinBox,
                            QComboBox, QPushButton, QFormLayout, QDialogButtonBox,
                            QFileDialog, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, QSettings

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for the CreepyAI application."""
    
    def __init__(self, config_manager, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("CreepyAI Settings")
        self.resize(600, 400)
        self.config_manager = config_manager
        
        # Set up UI
        self._setup_ui()
        
        # Load current settings
        self._load_settings()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # General settings tab
        self.general_tab = QWidget()
        general_layout = QFormLayout()
        
        # General settings
        self.data_dir = QLineEdit()
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_data_dir)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.data_dir)
        dir_layout.addWidget(browse_button)
        
        general_layout.addRow("Data Directory:", dir_layout)
        
        self.remember_recent = QCheckBox("Remember recent projects")
        general_layout.addRow("", self.remember_recent)
        
        self.max_recent = QSpinBox()
        self.max_recent.setMinimum(1)
        self.max_recent.setMaximum(20)
        general_layout.addRow("Maximum recent projects:", self.max_recent)
        
        self.general_tab.setLayout(general_layout)
        
        # Map settings tab
        self.map_tab = QWidget()
        map_layout = QFormLayout()
        
        self.map_provider = QComboBox()
        self.map_provider.addItems(["OpenStreetMap", "Google Maps", "Mapbox"])
        map_layout.addRow("Map Provider:", self.map_provider)
        
        self.api_key = QLineEdit()
        map_layout.addRow("API Key:", self.api_key)
        
        self.cache_maps = QCheckBox("Cache map tiles")
        map_layout.addRow("", self.cache_maps)
        
        self.map_tab.setLayout(map_layout)
        
        # Add tabs
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.map_tab, "Map")
        
        layout.addWidget(self.tabs)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def _load_settings(self):
        """Load current settings."""
        try:
            # Load from config manager
            if self.config_manager:
                data_dir = self.config_manager.get('data_dir', os.path.expanduser("~/.creepyai/data"))
                remember_recent = self.config_manager.get('remember_recent', True)
                max_recent = self.config_manager.get('max_recent', 10)
                map_provider = self.config_manager.get('map_provider', "OpenStreetMap")
                api_key = self.config_manager.get('map_api_key', "")
                cache_maps = self.config_manager.get('cache_maps', True)
                
                # Set values in UI
                self.data_dir.setText(data_dir)
                self.remember_recent.setChecked(remember_recent)
                self.max_recent.setValue(max_recent)
                index = self.map_provider.findText(map_provider)
                if index >= 0:
                    self.map_provider.setCurrentIndex(index)
                self.api_key.setText(api_key)
                self.cache_maps.setChecked(cache_maps)
            
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            QMessageBox.warning(self, "Settings Error", f"Failed to load settings: {str(e)}")
    
    def _save_settings(self):
        """Save settings and close dialog."""
        try:
            # Save to config manager
            if self.config_manager:
                self.config_manager.set('data_dir', self.data_dir.text())
                self.config_manager.set('remember_recent', self.remember_recent.isChecked())
                self.config_manager.set('max_recent', self.max_recent.value())
                self.config_manager.set('map_provider', self.map_provider.currentText())
                self.config_manager.set('map_api_key', self.api_key.text())
                self.config_manager.set('cache_maps', self.cache_maps.isChecked())
                
                # Save config to disk
                self.config_manager.save()
                
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            QMessageBox.critical(self, "Settings Error", f"Failed to save settings: {str(e)}")
    
    def _browse_data_dir(self):
        """Browse for data directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Data Directory", self.data_dir.text())
            
        if directory:
            self.data_dir.setText(directory)
