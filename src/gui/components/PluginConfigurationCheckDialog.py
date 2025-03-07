#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QListWidget, QListWidgetItem, QTextBrowser,
                           QDialogButtonBox, QProgressBar, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont

import time
import traceback

class PluginConfigurationCheckDialog(QDialog):
    """Dialog to check if all plugins are correctly configured"""
    
    def __init__(self, plugin_configs, parent=None):
        super(PluginConfigurationCheckDialog, self).__init__(parent)
        
        self.setWindowTitle("Plugin Configuration Check")
        self.setMinimumSize(700, 400)
        
        self.plugin_configs = plugin_configs
        self.check_results = {}
        
        self.setup_ui()
        
        # Start the check when dialog is shown
        self.run_checks()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Plugin Configuration Check")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header_label.setFont(font)
        layout.addWidget(header_label)
        
        # Description
        description_label = QLabel("Checking all plugins for valid configurations...")
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Splitter with plugin list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self.show_plugin_details)
        splitter.addWidget(self.plugin_list)
        
        # Details view
        self.details_view = QTextBrowser()
        splitter.addWidget(self.details_view)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 500])
        layout.addWidget(splitter)
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def run_checks(self):
        """Run configuration checks for all plugins"""
        # Initialize progress
        total_plugins = len(self.plugin_configs)
        progress_step = 100 // max(1, total_plugins)
        
        # Clear list
        self.plugin_list.clear()
        
        for i, (plugin_name, config) in enumerate(self.plugin_configs.items()):
            # Update progress
            self.progress_bar.setValue((i * progress_step))
            QApplication.processEvents()
            
            # Check configuration
            status, message = self.check_plugin_config(plugin_name, config)
            
            # Store results
            self.check_results[plugin_name] = {
                'status': status,
                'message': message
            }
            
            # Add to list with status indicator
            item = QListWidgetItem(plugin_name)
            if status == 'success':
                item.setForeground(QColor('green'))
                item.setIcon(QIcon.fromTheme('dialog-ok'))
            elif status == 'warning':
                item.setForeground(QColor('orange'))
                item.setIcon(QIcon.fromTheme('dialog-warning'))
            else:  # error
                item.setForeground(QColor('red'))
                item.setIcon(QIcon.fromTheme('dialog-error'))
            
            self.plugin_list.addItem(item)
        
        # Complete progress
        self.progress_bar.setValue(100)
        
        # Select first item if available
        if self.plugin_list.count() > 0:
            self.plugin_list.setCurrentRow(0)
    
    def check_plugin_config(self, plugin_name, config):
        """
        Check if a plugin configuration is valid
        
        This is a placeholder implementation. In a real application,
        this would perform actual validation based on plugin requirements.
        """
        try:
            # Simulate checking time
            time.sleep(0.2)
            
            # Basic checks
            if not config:
                return 'warning', "No configuration provided for this plugin."
            
            # Check for required fields based on plugin name
            if plugin_name.lower() in ['twitter', 'facebook', 'instagram']:
                required_fields = ['api_key', 'api_secret']
                for field in required_fields:
                    if field not in config or not config[field]:
                        return 'error', f"Missing required field: {field}"
            
            return 'success', "Plugin configuration appears valid."
        except Exception as e:
            return 'error', f"Error checking configuration: {str(e)}\n{traceback.format_exc()}"
    
    def show_plugin_details(self, current, previous):
        """Show details for the selected plugin"""
        if not current:
            self.details_view.clear()
            return
        
        plugin_name = current.text()
        result = self.check_results.get(plugin_name, {})
        
        # Build HTML details
        details = f"<h2>{plugin_name}</h2>"
        
        status = result.get('status', 'unknown')
        message = result.get('message', 'No check results available')
        
        # Add status with colored indicator
        if status == 'success':
            details += '<p style="color: green;"><b>Status: VALID</b></p>'
        elif status == 'warning':
            details += '<p style="color: orange;"><b>Status: WARNING</b></p>'
        else:  # error or unknown
            details += '<p style="color: red;"><b>Status: ERROR</b></p>'
        
        # Add message
        details += f"<p>{message}</p>"
        
        # Add configuration details
        config = self.plugin_configs.get(plugin_name, {})
        if config:
            details += "<h3>Configuration</h3>"
            details += "<table border='0' cellspacing='5' cellpadding='5'>"
            
            for key, value in config.items():
                # Mask sensitive values like API keys
                display_value = value
                if key.lower() in ['api_key', 'api_secret', 'password', 'token', 'key']:
                    if value:
                        display_value = value[:4] + '*' * (len(value) - 4)
                
                details += f"<tr><td><b>{key}</b></td><td>{display_value}</td></tr>"
            
            details += "</table>"
        else:
            details += "<p>No configuration settings found.</p>"
        
        self.details_view.setHtml(details)
