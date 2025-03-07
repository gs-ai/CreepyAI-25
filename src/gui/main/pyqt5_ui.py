#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyQt5 UI implementation for CreepyAI.

This module provides the main application UI using PyQt5.
"""

import os
import sys
import logging
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QAction, QToolBar,
    QStatusBar, QMenu, QFileDialog, QMessageBox, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDockWidget
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QPixmap

logger = logging.getLogger('CreepyAI.UI')

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("CreepyAI - OSINT Assistant")
        self.setMinimumSize(1024, 768)
        
        # Load settings
        self.settings = QSettings("CreepyAI", "OSINT")
        self.restore_geometry()
        
        # Set up UI components
        self.setup_ui()
        
        # Show status message
        self.statusBar().showMessage("Ready")
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_map_tab()
        self.create_analysis_tab()
        self.create_plugins_tab()
        
        # Create menu bar
        self.create_menus()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Welcome to CreepyAI")
        
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        welcome = QLabel("Welcome to CreepyAI")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(welcome)
        
        description = QLabel("OSINT Assistant for data collection and analysis")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-size: 18px; margin-bottom: 40px;")
        layout.addWidget(description)
        
        # Quick actions section
        actions_layout = QHBoxLayout()
        
        # New Project button
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.on_new_project)
        actions_layout.addWidget(new_project_btn)
        
        # Open Project button
        open_project_btn = QPushButton("Open Project")
        open_project_btn.clicked.connect(self.on_open_project)
        actions_layout.addWidget(open_project_btn)
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.on_settings)
        actions_layout.addWidget(settings_btn)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard, "Dashboard")
        
    def create_map_tab(self):
        """Create the map tab."""
        map_widget = QWidget()
        layout = QVBoxLayout(map_widget)
        
        # Placeholder for map
        map_placeholder = QLabel("Map view will be displayed here")
        map_placeholder.setAlignment(Qt.AlignCenter)
        map_placeholder.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; padding: 20px;")
        layout.addWidget(map_placeholder)
        
        self.tab_widget.addTab(map_widget, "Map")
        
    def create_analysis_tab(self):
        """Create the analysis tab."""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Placeholder for analysis tools
        analysis_placeholder = QLabel("Analysis tools will be displayed here")
        analysis_placeholder.setAlignment(Qt.AlignCenter)
        analysis_placeholder.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; padding: 20px;")
        layout.addWidget(analysis_placeholder)
        
        self.tab_widget.addTab(analysis_widget, "Analysis")
        
    def create_plugins_tab(self):
        """Create the plugins tab."""
        plugins_widget = QWidget()
        layout = QVBoxLayout(plugins_widget)
        
        # Placeholder for plugins
        plugins_placeholder = QLabel("Plugins will be displayed here")
        plugins_placeholder.setAlignment(Qt.AlignCenter)
        plugins_placeholder.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; padding: 20px;")
        layout.addWidget(plugins_placeholder)
        
        self.tab_widget.addTab(plugins_widget, "Plugins")
        
    def create_menus(self):
        """Create the application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.on_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add actions to the toolbar
        new_action = QAction("New", self)
        new_action.triggered.connect(self.on_new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.on_open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.on_save)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.on_settings)
        toolbar.addAction(settings_action)
        
    def restore_geometry(self):
        """Restore window size and position from settings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            # Default position and size
            self.setGeometry(100, 100, 1200, 800)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)
        
    # Action handlers
    def on_new_project(self):
        """Handle new project action."""
        QMessageBox.information(self, "New Project", "Creating a new project...")
        
    def on_open_project(self):
        """Handle open project action."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", 
            "CreepyAI Projects (*.creepy);;All Files (*)", 
            options=options
        )
        if file_name:
            QMessageBox.information(self, "Open Project", f"Opening project: {file_name}")
            
    def on_save(self):
        """Handle save action."""
        QMessageBox.information(self, "Save", "Saving project...")
        
    def on_save_as(self):
        """Handle save as action."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", 
            "CreepyAI Projects (*.creepy);;All Files (*)", 
            options=options
        )
        if file_name:
            QMessageBox.information(self, "Save As", f"Saving project as: {file_name}")
            
    def on_settings(self):
        """Handle settings action."""
        QMessageBox.information(self, "Settings", "Opening settings...")
        
    def on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, 
            "About CreepyAI",
            "CreepyAI - OSINT Assistant\n\n"
            "Version: 1.0\n\n"
            "A tool for gathering, analyzing, and visualizing OSINT data.\n\n"
            "© 2025 CreepyAI Team"
        )


def main():
    """Main entry point for the PyQt5 UI."""
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("CreepyAI")
    app.setOrganizationName("CreepyAI Team")
    
    # Create the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
