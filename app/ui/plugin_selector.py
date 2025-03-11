"""
Plugin Selector UI
Handles UI for selecting and configuring plugins
"""

import os
import logging
from typing import Dict, List, Any, Callable

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel, 
    QGroupBox, QFormLayout, QLineEdit, QFileDialog, QScrollArea,
    QFrame, QHBoxLayout, QComboBox, QDateEdit, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt5.QtGui import QIcon, QPixmap

from app.plugin_registry import instantiate_plugins
from app.controllers.map_controller import MapController

logger = logging.getLogger(__name__)

class PluginSelector(QWidget):
    """Widget for selecting which plugins to use and configuring them"""
    
    # Signal emitted when plugin visibility is changed
    pluginVisibilityChanged = pyqtSignal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins = instantiate_plugins()
        self.plugin_checkboxes = {}
        self.plugin_config_widgets = {}
        self.plugin_config_buttons = {}
        
        # Path to plugin icons
        self.icons_path = os.path.join("app", "resources", "icons")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create a scroll area for the plugin list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Add plugin categories
        self._add_plugin_category("Social Media Plugins", [
            plugin for plugin in self.plugins if plugin.name in [
                "Facebook", "Instagram", "LinkedIn", "Pinterest", 
                "Snapchat", "TikTok", "Twitter", "Yelp"
            ]
        ], scroll_layout)
        
        # Add other categories in the future
        # self._add_plugin_category("Other Plugins", [...], scroll_layout)
        
        # Add a "Configure All" button
        configure_all_btn = QPushButton("Configure All Plugins")
        configure_all_btn.clicked.connect(self._configure_all_plugins)
        main_layout.addWidget(configure_all_btn)
        
        # Add a note about attribution
        attribution_label = QLabel(
            "<small>Social media icons provided by <a href='https://icons8.com'>Icons8</a></small>"
        )
        attribution_label.setAlignment(Qt.AlignCenter)
        attribution_label.setOpenExternalLinks(True)
        main_layout.addWidget(attribution_label)
    
    def _add_plugin_category(self, category_name: str, plugins: List, layout: QVBoxLayout):
        """Add a category of plugins to the UI"""
        if not plugins:
            return
            
        # Create group box for the category
        group_box = QGroupBox(category_name)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        # Add each plugin in the category
        for plugin in plugins:
            plugin_frame = QFrame()
            plugin_layout = QHBoxLayout(plugin_frame)
            plugin_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add icon if available
            icon_path = os.path.join(self.icons_path, f"{plugin.name.lower()}-icon.png")
            if os.path.exists(icon_path):
                icon_label = QLabel()
                icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                plugin_layout.addWidget(icon_label)
            
            # Checkbox to enable/disable the plugin on map
            checkbox = QCheckBox(plugin.name)
            checkbox.setChecked(False)  # Default to unchecked
            checkbox.stateChanged.connect(lambda state, p=plugin.name: 
                self.pluginVisibilityChanged.emit(p, state == Qt.Checked))
            self.plugin_checkboxes[plugin.name] = checkbox
            plugin_layout.addWidget(checkbox, 1)
            
            # Configuration button
            config_btn = QPushButton("Configure")
            config_btn.clicked.connect(lambda _, p=plugin: self._configure_plugin(p))
            self.plugin_config_buttons[plugin.name] = config_btn
            plugin_layout.addWidget(config_btn)
            
            group_layout.addWidget(plugin_frame)
    
    def _configure_plugin(self, plugin):
        """Open the configuration dialog for a specific plugin"""
        config_dialog = PluginConfigDialog(plugin, self)
        result = config_dialog.exec_()
        
        if result == QDialog.Accepted:
            # Update the plugin's status
            is_configured, message = plugin.is_configured()
            checkbox = self.plugin_checkboxes.get(plugin.name)
            if checkbox:
                checkbox.setEnabled(is_configured)
                if not is_configured:
                    checkbox.setChecked(False)
                    self.pluginVisibilityChanged.emit(plugin.name, False)
    
    def _configure_all_plugins(self):
        """Open configuration dialogs for all plugins"""
        for plugin in self.plugins:
            self._configure_plugin(plugin)
    
    def connect_to_map_controller(self, map_controller: MapController):
        """Connect this selector to a map controller"""
        self.pluginVisibilityChanged.connect(map_controller.update_visible_plugins)

class PluginConfigDialog(QDialog):
    """Dialog for configuring a plugin"""
    
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.config_widgets = {}
        
        self.setWindowTitle(f"Configure {plugin.name}")
        self.resize(500, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Plugin name and description
        layout.addWidget(QLabel(f"<h3>{self.plugin.name}</h3>"))
        layout.addWidget(QLabel(self.plugin.description))
        layout.addWidget(QLabel("<hr>"))
        
        # Configuration form
        form_group = QGroupBox("Configuration Options")
        form_layout = QFormLayout()
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Add configuration options
        config_options = self.plugin.get_configuration_options()
        for option in config_options:
            widget = self._create_config_widget(option)
            if widget:
                form_layout.addRow(option["display_name"], widget)
                self.config_widgets[option["name"]] = widget
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def _create_config_widget(self, option):
        """Create a widget for a configuration option based on its type"""
        widget = None
        option_type = option["type"]
        
        if option_type == "string":
            widget = QLineEdit()
            widget.setText(str(option.get("default", "")))
        
        elif option_type == "boolean":
            widget = QCheckBox()
            widget.setChecked(bool(option.get("default", False)))
        
        elif option_type == "directory":
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            line_edit = QLineEdit()
            line_edit.setText(str(option.get("default", "")))
            browse_button = QPushButton("Browse...")
            
            layout.addWidget(line_edit)
            layout.addWidget(browse_button)
            
            browse_button.clicked.connect(
                lambda: line_edit.setText(QFileDialog.getExistingDirectory(
                    self, f"Select {option['display_name']}", line_edit.text()
                ))
            )
            
            # Store the line edit as the actual value widget
            widget.valueWidget = line_edit
        
        elif option_type == "file":
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            line_edit = QLineEdit()
            line_edit.setText(str(option.get("default", "")))
            browse_button = QPushButton("Browse...")
            
            layout.addWidget(line_edit)
            layout.addWidget(browse_button)
            
            browse_button.clicked.connect(
                lambda: line_edit.setText(QFileDialog.getOpenFileName(
                    self, f"Select {option['display_name']}", line_edit.text()
                )[0])
            )
            
            # Store the line edit as the actual value widget
            widget.valueWidget = line_edit
        
        return widget
    
    def save_config(self):
        """Save the configuration to the plugin"""
        config = {}
        for name, widget in self.config_widgets.items():
            # Handle different widget types
            if isinstance(widget, QLineEdit):
                config[name] = widget.text()
            elif isinstance(widget, QCheckBox):
                config[name] = widget.isChecked()
            elif hasattr(widget, 'valueWidget'):
                # For compound widgets like directory/file selectors
                if isinstance(widget.valueWidget, QLineEdit):
                    config[name] = widget.valueWidget.text()
        
        # Set configuration on plugin
        self.plugin.update_config(config)
        
        # Check if plugin is now configured
        is_configured, message = self.plugin.is_configured()
        if is_configured:
            self.accept()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Configuration Error", 
                                f"Plugin configuration is incomplete: {message}")
