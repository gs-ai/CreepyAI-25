#!/usr/bin/env python3
"""
Plugin configuration dialog for CreepyAI
"""
import os
import sys
import logging
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton,
    QFileDialog, QSpinBox, QDoubleSpinBox, QTextEdit
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class PluginConfigDialog(QDialog):
    """Dialog for configuring a plugin"""
    
    def __init__(self, parent, plugin):
        super(PluginConfigDialog, self).__init__(parent)
        
        self.plugin = plugin
        self.config_options = []
        self.config_widgets = {}
        
        # Get plugin info
        if hasattr(plugin, 'get_info'):
            self.plugin_info = plugin.get_info()
        else:
            self.plugin_info = {
                'name': getattr(plugin, 'name', 'Unknown Plugin'),
                'description': getattr(plugin, 'description', 'No description'),
                'version': getattr(plugin, 'version', '1.0.0'),
                'author': getattr(plugin, 'author', 'Unknown')
            }
        
        # Get configuration options
        if hasattr(plugin, 'get_configuration_options'):
            self.config_options = plugin.get_configuration_options()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        # Set window properties
        self.setWindowTitle(f"Configure {self.plugin_info['name']}")
        self.resize(400, 300)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add header with plugin info
        header_text = f"<h3>{self.plugin_info['name']} v{self.plugin_info['version']}</h3>"
        header_text += f"<p>{self.plugin_info['description']}</p>"
        header_text += f"<p>Author: {self.plugin_info['author']}</p>"
        
        header_label = QLabel(header_text)
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Form for configuration options
        form_layout = QFormLayout()
        
        # If no configuration options are defined, show a message
        if not self.config_options:
            form_layout.addRow(QLabel("This plugin has no configurable options."))
        
        # Add configuration options
        for option in self.config_options:
            option_name = option.get('name')
            option_type = option.get('type', 'string')
            option_default = option.get('default', '')
            option_required = option.get('required', False)
            option_label = option.get('display_name', option_name)
            option_description = option.get('description', '')
            
            # Check if we have a current value for this option
            current_value = None
            if hasattr(self.plugin, 'config') and isinstance(self.plugin.config, dict):
                current_value = self.plugin.config.get(option_name, option_default)
            
            # Create widget based on option type
            widget = None
            
            if option_type == 'string':
                widget = QLineEdit()
                widget.setText(str(current_value) if current_value is not None else str(option_default))
                
            elif option_type == 'boolean':
                widget = QCheckBox()
                widget.setChecked(bool(current_value) if current_value is not None else bool(option_default))
                
            elif option_type == 'file':
                widget = QLineEdit()
                widget.setText(str(current_value) if current_value is not None else str(option_default))
                
                # Add browse button
                browse_button = QPushButton("Browse...")
                browse_button.clicked.connect(lambda checked=False, w=widget: self._browse_file(w))
                
                # Create a container for the widget and browse button
                from PyQt5.QtWidgets import QHBoxLayout, QWidget
                container = QWidget()
                container_layout = QHBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(widget)
                container_layout.addWidget(browse_button)
                
                widget = container
                
            elif option_type == 'directory':
                widget = QLineEdit()
                widget.setText(str(current_value) if current_value is not None else str(option_default))
                
                # Add browse button
                browse_button = QPushButton("Browse...")
                browse_button.clicked.connect(lambda checked=False, w=widget.children()[1]: self._browse_directory(w))
                
                # Create a container for the widget and browse button
                from PyQt5.QtWidgets import QHBoxLayout, QWidget
                container = QWidget()
                container_layout = QHBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(widget)
                container_layout.addWidget(browse_button)
                
                widget = container
                
            elif option_type == 'integer':
                widget = QSpinBox()
                widget.setRange(-1000000, 1000000)
                widget.setValue(int(current_value) if current_value is not None else int(option_default))
                
            elif option_type == 'float':
                widget = QDoubleSpinBox()
                widget.setRange(-1000000.0, 1000000.0)
                widget.setValue(float(current_value) if current_value is not None else float(option_default))
                
            elif option_type == 'text':
                widget = QTextEdit()
                widget.setText(str(current_value) if current_value is not None else str(option_default))
                
            elif option_type == 'choice':
                widget = QComboBox()
                choices = option.get('choices', [])
                widget.addItems(choices)
                
                # Set current value
                if current_value is not None and current_value in choices:
                    widget.setCurrentText(current_value)
                elif option_default in choices:
                    widget.setCurrentText(option_default)
            
            # Add the widget to the form
            if widget:
                # Store the widget for later
                self.config_widgets[option_name] = widget
                
                # Add to form
                form_layout.addRow(f"{option_label}:", widget)
                
                # Add description as tooltip if available
                if option_description:
                    widget.setToolTip(option_description)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _browse_file(self, widget):
        """Show file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", widget.text()
        )
        if file_path:
            widget.setText(file_path)
            
    def _browse_directory(self, widget):
        """Show directory browser dialog"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Directory", widget.text()
        )
        if dir_path:
            widget.setText(dir_path)
    
    def accept(self):
        """Called when the user accepts the dialog"""
        # Get values from widgets
        config = {}
        
        for option in self.config_options:
            option_name = option.get('name')
            option_type = option.get('type', 'string')
            
            if option_name in self.config_widgets:
                widget = self.config_widgets[option_name]
                
                # Get value based on widget type
                value = None
                
                if option_type == 'string':
                    value = widget.text()
                    
                elif option_type == 'boolean':
                    value = widget.isChecked()
                    
                elif option_type == 'file' or option_type == 'directory':
                    # For file/directory widgets, the actual text field is the child widget
                    if hasattr(widget, 'children') and len(widget.children()) > 1:
                        child_widget = widget.children()[1]  # First child should be the QLineEdit
                        if isinstance(child_widget, QLineEdit):
                            value = child_widget.text()
                    
                elif option_type == 'integer':
                    value = widget.value()
                    
                elif option_type == 'float':
                    value = widget.value()
                    
                elif option_type == 'text':
                    value = widget.toPlainText()
                    
                elif option_type == 'choice':
                    value = widget.currentText()
                
                # Add to config
                config[option_name] = value
        
        # Apply configuration to plugin
        if hasattr(self.plugin, 'config'):
            # Update existing config
            if isinstance(self.plugin.config, dict):
                self.plugin.config.update(config)
            else:
                self.plugin.config = config
        else:
            # Set new config
            self.plugin.config = config
        
        # Call configure method if it exists
        if hasattr(self.plugin, 'configure'):
            try:
                self.plugin.configure()
            except Exception as e:
                logger.error(f"Error configuring plugin: {e}", exc_info=True)
        
        # Accept the dialog
        super(PluginConfigDialog, self).accept()
