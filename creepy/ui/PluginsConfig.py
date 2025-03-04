<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from creepy.resources.icons import Icons
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QStackedWidget, QWidget, QLabel, QCheckBox, QSpinBox, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QMessageBox, QComboBox,
    QTabWidget, QSlider
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon

from creepy.components.PluginConfigurationCheckDialog import PluginConfigurationCheckDialog

logger = logging.getLogger(__name__)

class PluginsConfigDialog(QDialog):
    """Dialog for configuring plugins settings."""
    
    def __init__(self, plugin_manager, config_manager, parent=None):
        super(PluginsConfigDialog, self).__init__(parent)
        self.setWindowTitle("Plugin Configuration")
        self.resize(800, 600)
        
        self.plugin_manager = plugin_manager
        self.config_manager = config_manager
        
        self._setup_ui()
        self._load_plugins()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        try:
            # Main layout
            main_layout = QVBoxLayout(self)
            
            # Create layout for list and stacked widget
            content_layout = QHBoxLayout()
            
            # Left side:
            self.plugin_list = QListWidget()
            self.plugin_list.setMaximumWidth(200)
            self.plugin_list.currentRowChanged.connect(self._change_plugin)
            content_layout.addWidget(self.plugin_list)
            
            # Right side:
            self.plugin_stack = QStackedWidget()
            content_layout.addWidget(self.plugin_stack)
            
            main_layout.addLayout(content_layout)
            
            # Action buttons
            button_layout = QHBoxLayout()
            
            self.import_button = QPushButton("Import Plugin...")
            button_layout.addWidget(self.import_button)
            
            self.check_button = QPushButton("Check Configurations")
            self.check_button.clicked.connect(self._check_configurations)
            button_layout.addWidget(self.check_button)
            
            button_layout.addStretch()
            
            main_layout.addLayout(button_layout)
            
            # Dialog buttons
            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
            self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self._apply_changes)
            main_layout.addWidget(self.button_box)
        
        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
    
    def _load_plugins(self):
        """Load and display available plugins."""
        try:
            # Clear existing items
            self.plugin_list.clear()
            
            # Remove all widgets from stack
            while self.plugin_stack.count() > 0:
                widget = self.plugin_stack.widget(0)
                self.plugin_stack.removeWidget(widget)
                widget.deleteLater()
            
            # Load available plugins
            for plugin_info in self.plugin_manager.get_all_plugins():
                # Add to list widget
                item = QListWidgetItem(plugin_info.name)
                self.plugin_list.addItem(item)
                
                # Create config widget for this plugin
                config_widget = PluginConfigWidget(plugin_info, self.plugin_manager)
                self.plugin_stack.addWidget(config_widget)
            
            # Select first item if available
            if self.plugin_list.count() > 0:
                self.plugin_list.setCurrentRow(0)
        
        except Exception as e:
            logger.error(f"Error loading plugins: {e}")
    
    def _change_plugin(self, row):
        """Change the displayed plugin configuration."""
        try:
            if row >= 0 and row < self.plugin_stack.count():
                self.plugin_stack.setCurrentIndex(row)
        
        except Exception as e:
            logger.error(f"Error changing plugin: {e}")
    
    def _check_configurations(self):
        """Check if all plugins are properly configured."""
        try:
            configs_to_check = {}
            
            # Collect configurations from all plugin widgets
            for i in range(self.plugin_stack.count()):
                plugin_widget = self.plugin_stack.widget(i)
                plugin_name = self.plugin_list.item(i).text()
                configs_to_check[plugin_name] = plugin_widget.get_config()
            
            # Show check dialog
            check_dialog = PluginConfigurationCheckDialog(configs_to_check, self)
            check_dialog.exec_()
        
        except Exception as e:
            logger.error(f"Error checking configurations: {e}")
    
    def _apply_changes(self):
        """Apply configuration changes."""
        try:
            for i in range(self.plugin_stack.count()):
                plugin_widget = self.plugin_stack.widget(i)
                plugin_name = self.plugin_list.item(i).text()
                
                if plugin_widget.is_modified():
                    config = plugin_widget.get_config()
                    self.plugin_manager.save_plugin_config(plugin_name, config)
                    plugin_widget.mark_saved()
            
            QMessageBox.information(self, "Configuration Saved",
                                  "Plugin configurations have been saved successfully.")
        
        except Exception as e:
            logger.error(f"Error applying changes: {e}")
    
    def accept(self):
        """Override accept to save changes before closing."""
        self._apply_changes()
        super().accept()


class PluginConfigWidget(QWidget):
    """Widget for configuring a single plugin."""
    
    def __init__(self, plugin_info, plugin_manager):
        super(PluginConfigWidget, self).__init__()
        
        self.plugin_info = plugin_info
        self.plugin_manager = plugin_manager
        self.modified = False
        
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self):
        """Set up the configuration widget UI."""
        layout = QVBoxLayout(self)
        
        # Plugin header
        name_label = QLabel(self.plugin_info.name)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        name_label.setFont(font)
        layout.addWidget(name_label)
        
        # Plugin description
        desc_label = QLabel(self.plugin_info.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Status and activation controls
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.active_checkbox = QCheckBox("Active")
        self.active_checkbox.setChecked(self.plugin_info.active)
        self.active_checkbox.stateChanged.connect(self._mark_modified)
        status_layout.addWidget(self.active_checkbox)
        
        layout.addLayout(status_layout)
        
        # Configuration form
        self.config_form = QFormLayout()
        layout.addLayout(self.config_form)
        
        self.setLayout(layout)
    
    def _load_config(self):
        """Load the plugin configuration."""
        config = self.plugin_manager.get_plugin_config(self.plugin_info.name)
        
        for key, value in config.items():
            line_edit = QLineEdit(value)
            line_edit.textChanged.connect(self._mark_modified)
            self.config_form.addRow(QLabel(key), line_edit)
    
    def get_config(self):
        """Get the current configuration."""
        config = {}
        
        for i in range(self.config_form.rowCount()):
            label = self.config_form.itemAt(i, QFormLayout.LabelRole).widget()
            line_edit = self.config_form.itemAt(i, QFormLayout.FieldRole).widget()
            config[label.text()] = line_edit.text()
        
        return config
    
    def _mark_modified(self):
        """Mark the configuration as modified."""
        self.modified = True
    
    def is_modified(self):
        """Check if the configuration is modified."""
        return self.modified
    
    def mark_saved(self):
        """Mark the configuration as saved."""
        self.modified = False


if __name__ == "__main__":
    import sys
    from creepy.plugin_manager import PluginManager
    
    app = QtWidgets.QApplication(sys.argv)
    plugin_manager = PluginManager()
    dialog = PluginsConfigDialog(plugin_manager)
    dialog.show()
=======
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\pluginsConfig.ui'
#
# Created: Fri Jan 31 15:31:51 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = lambda s: s

class Ui_PluginsConfigurationDialog(object):
    def setupUi(self, PluginsConfigurationDialog):
        PluginsConfigurationDialog.setObjectName(_fromUtf8("PluginsConfigurationDialog"))
        PluginsConfigurationDialog.resize(810, 640)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PluginsConfigurationDialog.sizePolicy().hasHeightForWidth())
        PluginsConfigurationDialog.setSizePolicy(sizePolicy)
        PluginsConfigurationDialog.setMinimumSize(QtCore.QSize(810, 640))
        PluginsConfigurationDialog.setMaximumSize(QtCore.QSize(810, 640))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/properties")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        PluginsConfigurationDialog.setWindowIcon(icon)
        self.BtnBox = QtWidgets.QDialogButtonBox(PluginsConfigurationDialog)
        self.BtnBox.setGeometry(QtCore.QRect(430, 600, 341, 32))
        self.BtnBox.setOrientation(QtCore.Qt.Horizontal)
        self.BtnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnBox.setObjectName(_fromUtf8("BtnBox"))
        self.PluginsList = QtWidgets.QListView(PluginsConfigurationDialog)
        self.PluginsList.setGeometry(QtCore.QRect(10, 10, 211, 581))
        self.PluginsList.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.PluginsList.setObjectName(_fromUtf8("PluginsList"))

        self.retranslateUi(PluginsConfigurationDialog)
        QtCore.QObject.connect(self.BtnBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PluginsConfigurationDialog.accept)
        QtCore.QObject.connect(self.BtnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PluginsConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PluginsConfigurationDialog)

    def retranslateUi(self, PluginsConfigurationDialog):
        PluginsConfigurationDialog.setWindowTitle(QtWidgets.QApplication.translate("PluginsConfigurationDialog", "Plugins Configuration", None))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PluginsConfigurationDialog = QtWidgets.QDialog()
    ui = Ui_PluginsConfigurationDialog()
    ui.setupUi(PluginsConfigurationDialog)
    PluginsConfigurationDialog.show()
>>>>>>> gs-ai-patch-1
    sys.exit(app.exec_())
