"""
Import Dialog for CreepyAI
Allows users to import data from various sources
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QComboBox,
    QGroupBox, QCheckBox, QDialogButtonBox, QSplitter,
    QFrame, QRadioButton, QButtonGroup, QTreeWidget,
    QTreeWidgetItem, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from app.core.include.button_styles import ButtonStyles
from app.core.include.constants import SOCIAL_MEDIA_ICONS
from app.plugin_registry import get_plugin_by_name, get_plugin_names

logger = logging.getLogger(__name__)

class ImportDialog(QDialog):
    """Dialog for importing data from various sources"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Data")
        self.resize(700, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.selected_plugin = None
        self.selected_files = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create a horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - source selection
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Import source type selection
        source_group = QGroupBox("Import Source")
        source_layout = QVBoxLayout(source_group)
        
        self.source_button_group = QButtonGroup(self)
        
        self.file_radio = QRadioButton("From Files")
        self.file_radio.setChecked(True)
        self.source_button_group.addButton(self.file_radio)
        source_layout.addWidget(self.file_radio)
        
        self.folder_radio = QRadioButton("From Folder")
        self.source_button_group.addButton(self.folder_radio)
        source_layout.addWidget(self.folder_radio)
        
        self.url_radio = QRadioButton("From URL")
        self.source_button_group.addButton(self.url_radio)
        source_layout.addWidget(self.url_radio)
        
        self.source_button_group.buttonClicked.connect(self.source_type_changed)
        
        left_layout.addWidget(source_group)
        
        # File selection
        self.file_group = QGroupBox("Files")
        file_layout = QVBoxLayout(self.file_group)
        
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        
        file_buttons_layout = QHBoxLayout()
        
        self.add_files_btn = QPushButton("Add Files...")
        self.add_files_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "add-icon.png")))
        ButtonStyles.secondary_button(self.add_files_btn)
        self.add_files_btn.clicked.connect(self.add_files)
        file_buttons_layout.addWidget(self.add_files_btn)
        
        self.remove_file_btn = QPushButton("Remove")
        self.remove_file_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "remove-icon.png")))
        ButtonStyles.danger_button(self.remove_file_btn)
        self.remove_file_btn.clicked.connect(self.remove_file)
        self.remove_file_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.remove_file_btn)
        
        file_layout.addLayout(file_buttons_layout)
        
        left_layout.addWidget(self.file_group)
        
        # Plugin selection
        plugin_group = QGroupBox("Plugin")
        plugin_layout = QVBoxLayout(plugin_group)
        
        plugin_layout.addWidget(QLabel("Select a plugin to process the data:"))
        
        self.plugin_combo = QComboBox()
        self.populate_plugins()
        plugin_layout.addWidget(self.plugin_combo)
        
        left_layout.addWidget(plugin_group)
        
        # Add the left widget to the splitter
        splitter.addWidget(left_widget)
        
        # Right side - options and preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Plugin info
        plugin_info_group = QGroupBox("Plugin Information")
        plugin_info_layout = QVBoxLayout(plugin_info_group)
        
        self.plugin_icon_label = QLabel()
        self.plugin_icon_label.setAlignment(Qt.AlignCenter)
        plugin_info_layout.addWidget(self.plugin_icon_label)
        
        self.plugin_name_label = QLabel()
        self.plugin_name_label.setAlignment(Qt.AlignCenter)
        plugin_info_layout.addWidget(self.plugin_name_label)
        
        self.plugin_desc_label = QLabel()
        self.plugin_desc_label.setAlignment(Qt.AlignCenter)
        self.plugin_desc_label.setWordWrap(True)
        plugin_info_layout.addWidget(self.plugin_desc_label)
        
        right_layout.addWidget(plugin_info_group)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        self.geocode_checkbox = QCheckBox("Geocode addresses")
        self.geocode_checkbox.setChecked(True)
        options_layout.addWidget(self.geocode_checkbox)
        
        self.dedup_checkbox = QCheckBox("Remove duplicate entries")
        self.dedup_checkbox.setChecked(True)
        options_layout.addWidget(self.dedup_checkbox)
        
        self.timezone_checkbox = QCheckBox("Normalize timestamps to local timezone")
        self.timezone_checkbox.setChecked(True)
        options_layout.addWidget(self.timezone_checkbox)
        
        right_layout.addWidget(options_group)
        
        # Add the right widget to the splitter
        splitter.addWidget(right_widget)
        
        # Add splitter to main layout with 40/60 ratio
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)
        
        # Add buttons at the bottom
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ButtonStyles.primary_button(ok_button)
        ok_button.setText("Import")
        
        # Connect signals
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Update plugin info
        self.plugin_combo.currentIndexChanged.connect(self.update_plugin_info)
        self.update_plugin_info()
        
        # Connect file selection change
        self.file_list.itemSelectionChanged.connect(self.update_remove_button)
    
    def populate_plugins(self):
        """Populate the plugin selection dropdown"""
        self.plugin_combo.clear()
        
        try:
            plugin_names = get_plugin_names()
            self.plugin_combo.addItems(plugin_names)
        except Exception as e:
            logger.error(f"Error loading plugins: {e}")
            # Add some dummy plugins for UI testing
            self.plugin_combo.addItems([
                "Facebook",
                "Instagram", 
                "Twitter",
                "LinkedIn",
                "Snapchat"
            ])
    
    def update_plugin_info(self):
        """Update the plugin information display"""
        plugin_name = self.plugin_combo.currentText()
        self.selected_plugin = plugin_name
        
        if not plugin_name:
            self.plugin_name_label.setText("No plugin selected")
            self.plugin_desc_label.setText("")
            self.plugin_icon_label.clear()
            return
        
        self.plugin_name_label.setText(plugin_name)
        
        # Try to get the plugin description from the plugin registry
        try:
            plugin = get_plugin_by_name(plugin_name)
            if plugin:
                self.plugin_desc_label.setText(plugin.description)
            else:
                self.plugin_desc_label.setText("No description available")
        except Exception as e:
            logger.error(f"Error loading plugin info: {e}")
            self.plugin_desc_label.setText("Plugin information unavailable")
        
        # Load icon if available
        icon_name = SOCIAL_MEDIA_ICONS.get(plugin_name, "plugin-icon.png")
        icon_path = os.path.join("app", "resources", "icons", icon_name)
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.plugin_icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.plugin_icon_label.setText("No icon")
    
    def source_type_changed(self, button):
        """Handle source type selection change"""
        is_file_mode = self.file_radio.isChecked()
        is_folder_mode = self.folder_radio.isChecked()
        is_url_mode = self.url_radio.isChecked()
        
        # Update UI based on selection
        self.file_group.setVisible(is_file_mode or is_folder_mode)
        
        # Update button text
        if is_file_mode:
            self.add_files_btn.setText("Add Files...")
        elif is_folder_mode:
            self.add_files_btn.setText("Add Folder...")
    
    def add_files(self):
        """Add files or folder to the import list"""
        if self.file_radio.isChecked():
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files to Import", "", "All Files (*)"
            )
            
            for file_path in files:
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                self.file_list.addItem(item)
                self.selected_files.append(file_path)
                
        elif self.folder_radio.isChecked():
            folder = QFileDialog.getExistingDirectory(
                self, "Select Folder to Import"
            )
            
            if folder:
                item = QListWidgetItem(os.path.basename(folder) + "/")
                item.setData(Qt.UserRole, folder)
                self.file_list.addItem(item)
                self.selected_files.append(folder)
    
    def remove_file(self):
        """Remove selected file from the list"""
        selected_items = self.file_list.selectedItems()
        
        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
    
    def update_remove_button(self):
        """Update the state of the remove button based on selection"""
        self.remove_file_btn.setEnabled(len(self.file_list.selectedItems()) > 0)
    
    def get_selected_files(self) -> List[str]:
        """Get the list of selected files/folders"""
        return self.selected_files
    
    def get_selected_plugin(self) -> str:
        """Get the name of the selected plugin"""
        return self.selected_plugin
    
    def accept(self) -> None:
        """Called when the dialog is accepted"""
        # Make sure we have files and a plugin selected
        if not self.selected_files:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "No Data Selected", 
                "Please select at least one file or folder to import."
            )
            return
            
        if not self.selected_plugin:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "No Plugin Selected", 
                "Please select a plugin to process the data."
            )
            return
            
        super().accept()
