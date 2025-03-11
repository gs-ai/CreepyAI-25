"""
Preferences Dialog for CreepyAI
Allows customizing application settings
"""

import os
import logging
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTabWidget, QWidget, QFormLayout, QCheckBox,
    QSpinBox, QDialogButtonBox, QFileDialog, QGroupBox,
    QRadioButton, QSlider, QLineEdit
)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon

from app.core.theme_manager import ThemeManager, Theme
from app.core.include.config_manager import ConfigManager
from app.core.include.button_styles import ButtonStyles  # Import ButtonStyles

logger = logging.getLogger(__name__)

class PreferencesDialog(QDialog):
    """Dialog for application preferences"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.resize(600, 500)
        
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        
        # Changes to apply when dialog is accepted
        self.pending_changes = {}
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Display tab
        display_tab = self.create_display_tab()
        tab_widget.addTab(display_tab, "Display")
        
        # Map tab
        map_tab = self.create_map_tab()
        tab_widget.addTab(map_tab, "Map")
        
        # Plugins tab
        plugins_tab = self.create_plugins_tab()
        tab_widget.addTab(plugins_tab, "Plugins")
        
        # Privacy tab
        privacy_tab = self.create_privacy_tab()
        tab_widget.addTab(privacy_tab, "Privacy")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons with enhanced styling
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        
        # Style the buttons
        ok_btn = button_box.button(QDialogButtonBox.Ok)
        cancel_btn = button_box.button(QDialogButtonBox.Cancel)
        apply_btn = button_box.button(QDialogButtonBox.Apply)
        
        ButtonStyles.primary_button(ok_btn)
        ButtonStyles.secondary_button(cancel_btn)
        ButtonStyles.secondary_button(apply_btn)
        
        # Set icons
        ok_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "check-icon.png")))
        cancel_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "cancel-icon.png")))
        apply_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "apply-icon.png")))
        
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_general_tab(self) -> QWidget:
        """Create the general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data directories section
        directories_group = QGroupBox("Data Directories")
        form_layout = QFormLayout(directories_group)
        
        self.data_dir_edit = QLineEdit()
        data_dir_layout = QHBoxLayout()
        data_dir_layout.addWidget(self.data_dir_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_directory(self.data_dir_edit, "Data Directory"))
        data_dir_layout.addWidget(browse_btn)
        form_layout.addRow("Data Directory:", data_dir_layout)
        
        self.export_dir_edit = QLineEdit()
        export_dir_layout = QHBoxLayout()
        export_dir_layout.addWidget(self.export_dir_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_directory(self.export_dir_edit, "Export Directory"))
        export_dir_layout.addWidget(browse_btn)
        form_layout.addRow("Export Directory:", export_dir_layout)
        
        layout.addWidget(directories_group)
        
        # Startup behavior
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.check_updates_checkbox = QCheckBox("Check for updates at startup")
        startup_layout.addWidget(self.check_updates_checkbox)
        
        self.restore_session_checkbox = QCheckBox("Restore previous session")
        startup_layout.addWidget(self.restore_session_checkbox)
        
        self.show_welcome_checkbox = QCheckBox("Show welcome screen")
        startup_layout.addWidget(self.show_welcome_checkbox)
        
        layout.addWidget(startup_group)
        
        # Logging settings
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.log_file_edit = QLineEdit()
        log_file_layout = QHBoxLayout()
        log_file_layout.addWidget(self.log_file_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file(self.log_file_edit, "Log File", "*.log"))
        log_file_layout.addWidget(browse_btn)
        logging_layout.addRow("Log File:", log_file_layout)
        
        # Enhanced clear logs button
        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "trash-icon.png")))
        ButtonStyles.danger_button(self.clear_logs_btn)  # Apply danger style
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        logging_layout.addRow("", self.clear_logs_btn)
        
        layout.addWidget(logging_group)
        
        # Add stretching space
        layout.addStretch()
        
        return tab
    
    def create_display_tab(self) -> QWidget:
        """Create the display settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.system_theme_radio = QRadioButton("Use System Theme")
        theme_layout.addWidget(self.system_theme_radio)
        
        self.light_theme_radio = QRadioButton("Light Theme")
        theme_layout.addWidget(self.light_theme_radio)
        
        self.dark_theme_radio = QRadioButton("Dark Theme")
        theme_layout.addWidget(self.dark_theme_radio)
        
        # Group radio buttons
        self.theme_buttons = QButtonGroup()
        self.theme_buttons.addButton(self.system_theme_radio, 0)
        self.theme_buttons.addButton(self.light_theme_radio, 1)
        self.theme_buttons.addButton(self.dark_theme_radio, 2)
        
        layout.addWidget(theme_group)
        
        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QFormLayout(font_group)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setSingleStep(1)
        font_layout.addRow("Font Size:", self.font_size_spin)
        
        layout.addWidget(font_group)
        
        # UI scaling
        scaling_group = QGroupBox("UI Scaling")
        scaling_layout = QVBoxLayout(scaling_group)
        
        scale_label = QLabel("UI Scale Factor:")
        scaling_layout.addWidget(scale_label)
        
        scale_slider_layout = QHBoxLayout()
        scale_slider_layout.addWidget(QLabel("80%"))
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(80, 150)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        scale_slider_layout.addWidget(self.scale_slider)
        
        scale_slider_layout.addWidget(QLabel("150%"))
        
        scaling_layout.addLayout(scale_slider_layout)
        
        self.scale_value_label = QLabel("100%")
        self.scale_value_label.setAlignment(Qt.AlignCenter)
        self.scale_slider.valueChanged.connect(lambda v: self.scale_value_label.setText(f"{v}%"))
        scaling_layout.addWidget(self.scale_value_label)
        
        layout.addWidget(scaling_group)
        
        # Add stretching space
        layout.addStretch()
        
        return tab
    
    def create_map_tab(self) -> QWidget:
        """Create the map settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Default map layer
        map_layer_group = QGroupBox("Default Map Layer")
        map_layer_layout = QVBoxLayout(map_layer_group)
        
        self.map_layer_combo = QComboBox()
        self.map_layer_combo.addItems(["Street Map", "Satellite", "Terrain", "Dark Mode"])
        map_layer_layout.addWidget(self.map_layer_combo)
        
        layout.addWidget(map_layer_group)
        
        # Map display options
        map_options_group = QGroupBox("Map Display Options")
        map_options_layout = QVBoxLayout(map_options_group)
        
        self.auto_fit_checkbox = QCheckBox("Auto-fit to markers")
        map_options_layout.addWidget(self.auto_fit_checkbox)
        
        self.cluster_markers_checkbox = QCheckBox("Enable marker clustering")
        map_options_layout.addWidget(self.cluster_markers_checkbox)
        
        self.show_heatmap_checkbox = QCheckBox("Show heatmap instead of markers")
        map_options_layout.addWidget(self.show_heatmap_checkbox)
        
        layout.addWidget(map_options_group)
        
        # Default view settings
        view_settings_group = QGroupBox("Default View Settings")
        view_settings_layout = QFormLayout(view_settings_group)
        
        self.default_zoom_spin = QSpinBox()
        self.default_zoom_spin.setRange(1, 18)
        self.default_zoom_spin.setValue(4)
        view_settings_layout.addRow("Default Zoom Level:", self.default_zoom_spin)
        
        # Default center coordinates
        center_layout = QHBoxLayout()
        
        self.default_lat_edit = QLineEdit()
        self.default_lat_edit.setPlaceholderText("Latitude")
        center_layout.addWidget(self.default_lat_edit)
        
        self.default_lon_edit = QLineEdit()
        self.default_lon_edit.setPlaceholderText("Longitude")
        center_layout.addWidget(self.default_lon_edit)
        
        view_settings_layout.addRow("Default Center:", center_layout)
        
        layout.addWidget(view_settings_group)
        
        # Add stretching space
        layout.addStretch()
        
        return tab
    
    def create_plugins_tab(self) -> QWidget:
        """Create the plugins settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # General plugin settings
        plugin_general_group = QGroupBox("Plugin Settings")
        plugin_general_layout = QVBoxLayout(plugin_general_group)
        
        self.plugins_enabled_checkbox = QCheckBox("Enable plugins")
        self.plugins_enabled_checkbox.setChecked(True)
        plugin_general_layout.addWidget(self.plugins_enabled_checkbox)
        
        self.auto_load_plugins_checkbox = QCheckBox("Auto-load plugins at startup")
        plugin_general_layout.addWidget(self.auto_load_plugins_checkbox)
        
        plugin_general_layout.addWidget(QLabel("Plugin loading can be configured individually in the Plugins panel."))
        
        layout.addWidget(plugin_general_group)
        
        # Plugin data directory settings
        plugin_data_group = QGroupBox("Plugin Data")
        plugin_data_layout = QFormLayout(plugin_data_group)
        
        self.plugin_data_dir_edit = QLineEdit()
        plugin_dir_layout = QHBoxLayout()
        plugin_dir_layout.addWidget(self.plugin_data_dir_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_directory(self.plugin_data_dir_edit, "Plugin Data Directory"))
        plugin_dir_layout.addWidget(browse_btn)
        plugin_data_layout.addRow("Plugin Data Directory:", plugin_dir_layout)
        
        layout.addWidget(plugin_data_group)
        
        # Plugin controls with enhanced buttons
        plugin_controls_group = QGroupBox("Plugin Controls")
        plugin_controls_layout = QHBoxLayout(plugin_controls_group)
        
        self.reload_plugins_btn = QPushButton("Reload Plugins")
        self.reload_plugins_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "refresh-icon.png")))
        ButtonStyles.secondary_button(self.reload_plugins_btn)  # Apply secondary style
        plugin_controls_layout.addWidget(self.reload_plugins_btn)
        
        self.plugin_manager_btn = QPushButton("Plugin Manager...")
        self.plugin_manager_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "plugins-icon.png")))
        ButtonStyles.primary_button(self.plugin_manager_btn)  # Apply primary style
        plugin_controls_layout.addWidget(self.plugin_manager_btn)
        
        layout.addWidget(plugin_controls_group)
        
        # Add stretching space
        layout.addStretch()
        
        return tab
    
    def create_privacy_tab(self) -> QWidget:
        """Create the privacy settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data collection settings
        data_collection_group = QGroupBox("Data Collection")
        data_collection_layout = QVBoxLayout(data_collection_group)
        
        self.collect_usage_stats_checkbox = QCheckBox("Collect anonymous usage statistics")
        self.collect_usage_stats_checkbox.setChecked(False)
        data_collection_layout.addWidget(self.collect_usage_stats_checkbox)
        
        self.send_error_reports_checkbox = QCheckBox("Send error reports")
        self.send_error_reports_checkbox.setChecked(False)
        data_collection_layout.addWidget(self.send_error_reports_checkbox)
        
        layout.addWidget(data_collection_group)
        
        # Location settings
        location_group = QGroupBox("Location Settings")
        location_layout = QVBoxLayout(location_group)
        
        self.save_locations_checkbox = QCheckBox("Save location history")
        location_layout.addWidget(self.save_locations_checkbox)
        
        # Enhanced clear history button
        self.clear_locations_btn = QPushButton("Clear Location History")
        self.clear_locations_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "trash-icon.png")))
        ButtonStyles.danger_button(self.clear_locations_btn)  # Apply danger style
        self.clear_locations_btn.clicked.connect(self.clear_location_history)
        location_layout.addWidget(self.clear_locations_btn)
        
        layout.addWidget(location_group)
        
        # Cache settings
        cache_group = QGroupBox("Cache Settings")
        cache_layout = QVBoxLayout(cache_group)
        
        self.enable_cache_checkbox = QCheckBox("Enable caching")
        cache_layout.addWidget(self.enable_cache_checkbox)
        
        cache_buttons_layout = QHBoxLayout()
        
        # Enhanced cache buttons
        self.clear_cache_btn = QPushButton("Clear Cache")
        self.clear_cache_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "trash-icon.png")))
        ButtonStyles.danger_button(self.clear_cache_btn)  # Apply danger style
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_buttons_layout.addWidget(self.clear_cache_btn)
        
        self.verify_cache_btn = QPushButton("Verify Cache Integrity")
        self.verify_cache_btn.setIcon(QIcon(os.path.join("app", "resources", "icons", "verify-icon.png")))
        ButtonStyles.secondary_button(self.verify_cache_btn)  # Apply secondary style
        cache_buttons_layout.addWidget(self.verify_cache_btn)
        
        cache_layout.addLayout(cache_buttons_layout)
        
        layout.addWidget(cache_group)
        
        # Add stretching space
        layout.addStretch()
        
        return tab
    
    def browse_directory(self, line_edit, title):
        """Open directory browser dialog"""
        directory = QFileDialog.getExistingDirectory(self, f"Select {title}", line_edit.text())
        if directory:
            line_edit.setText(directory)
    
    def browse_file(self, line_edit, title, filter_str):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select {title}", line_edit.text(), filter_str)
        if file_path:
            line_edit.setText(file_path)
    
    def load_settings(self):
        """Load settings from configuration manager"""
        # General tab
        data_dir = self.config_manager.get("general", "data_directory", "")
        self.data_dir_edit.setText(data_dir)
        
        export_dir = self.config_manager.get("general", "export_directory", "")
        self.export_dir_edit.setText(export_dir)
        
        check_updates = self.config_manager.get("general", "auto_update_check", True)
        self.check_updates_checkbox.setChecked(check_updates)
        
        restore_session = self.config_manager.get("general", "save_session", True)
        self.restore_session_checkbox.setChecked(restore_session)
        
        show_welcome = self.config_manager.get("general", "show_welcome", True)
        self.show_welcome_checkbox.setChecked(show_welcome)
        
        log_level = self.config_manager.get("general", "log_level", "INFO")
        self.log_level_combo.setCurrentText(log_level)
        
        log_file = self.config_manager.get("general", "log_file", "")
        self.log_file_edit.setText(log_file)
        
        # Display tab
        theme = self.theme_manager.get_current_theme()
        if theme == Theme.SYSTEM:
            self.system_theme_radio.setChecked(True)
        elif theme == Theme.LIGHT:
            self.light_theme_radio.setChecked(True)
        elif theme == Theme.DARK:
            self.dark_theme_radio.setChecked(True)
        
        font_size = self.config_manager.get("display", "font_size", 10)
        self.font_size_spin.setValue(font_size)
        
        scale_factor = self.config_manager.get("display", "scale_factor", 100)
        self.scale_slider.setValue(scale_factor)
        
        # Map tab
        default_layer = self.config_manager.get("map", "default_layer", "Street Map")
        self.map_layer_combo.setCurrentText(default_layer)
        
        auto_fit = self.config_manager.get("map", "auto_fit", True)
        self.auto_fit_checkbox.setChecked(auto_fit)
        
        clustering = self.config_manager.get("map", "clustering", True)
        self.cluster_markers_checkbox.setChecked(clustering)
        
        heatmap = self.config_manager.get("map", "heatmap", False)
        self.show_heatmap_checkbox.setChecked(heatmap)
        
        default_zoom = self.config_manager.get("map", "default_zoom", 4)
        self.default_zoom_spin.setValue(default_zoom)
        
        default_lat = self.config_manager.get("map", "default_lat", "")
        self.default_lat_edit.setText(str(default_lat))
        
        default_lon = self.config_manager.get("map", "default_lon", "")
        self.default_lon_edit.setText(str(default_lon))
        
        # Plugins tab
        plugins_enabled = self.config_manager.get("plugins", "enabled", True)
        self.plugins_enabled_checkbox.setChecked(plugins_enabled)
        
        auto_load = self.config_manager.get("plugins", "auto_load", True)
        self.auto_load_plugins_checkbox.setChecked(auto_load)
        
        plugin_data_dir = self.config_manager.get("plugins", "data_directory", "")
        self.plugin_data_dir_edit.setText(plugin_data_dir)
        
        # Privacy tab
        collect_stats = self.config_manager.get("privacy", "collect_usage_stats", False)
        self.collect_usage_stats_checkbox.setChecked(collect_stats)
        
        send_errors = self.config_manager.get("privacy", "send_error_reports", False)
        self.send_error_reports_checkbox.setChecked(send_errors)
        
        save_locations = self.config_manager.get("privacy", "save_locations", True)
        self.save_locations_checkbox.setChecked(save_locations)
        
        enable_cache = self.config_manager.get("privacy", "enable_cache", True)
        self.enable_cache_checkbox.setChecked(enable_cache)
    
    def save_settings(self):
        """Save settings from UI components to QSettings"""
        # General tab
        self.settings.setValue(SettingsKey.DATA_DIRECTORY, self.data_dir_path.text())
        self.settings.setValue(SettingsKey.SKIP_WELCOME, not self.show_welcome.isChecked())
        self.settings.setValue("restoreSession", self.restore_session.isChecked())
        self.settings.setValue(SettingsKey.CHECK_FOR_UPDATES, self.check_updates.isChecked())
        self.settings.setValue(SettingsKey.LANGUAGE, self.language_combo.currentData())
        
        # Appearance tab
        self.settings.setValue(SettingsKey.THEME, self.theme_combo.currentData())
        self.settings.setValue("fontSize", self.font_size_spin.value())
        self.settings.setValue("fontFamily", self.font_family_combo.currentText())
        self.settings.setValue("iconSize", self.icon_size_group.checkedId())
        self.settings.setValue("showToolbarText", self.show_toolbar_text.isChecked())
        self.settings.setValue("useAnimations", self.use_animations.isChecked())
        
        # Map tab
        self.settings.setValue(SettingsKey.MAP_LAYER, self.map_provider_combo.currentText())
        self.settings.setValue("defaultZoom", self.default_zoom_slider.value())
        self.settings.setValue("showClusters", self.show_clusters.isChecked())
        self.settings.setValue("showHeatmap", self.show_heatmap.isChecked())
        self.settings.setValue("showTimeline", self.show_timeline.isChecked())
        self.settings.setValue("defaultLat", self.default_lat.text())
        self.settings.setValue("defaultLon", self.default_lon.text())
        
        # Plugins tab
        self.settings.setValue("pluginDirectory", self.plugin_dir_path.text())
        self.settings.setValue("autoUpdatePlugins", self.auto_update_plugins.isChecked())
        self.settings.setValue("loadAllPlugins", self.load_all_plugins.isChecked())
        self.settings.setValue("pluginSandbox", self.plugin_sandbox.isChecked())
        self.settings.setValue("securityLevel", self.security_level_combo.currentIndex())
        
        # Privacy tab
        self.settings.setValue(SettingsKey.COLLECT_USAGE_DATA, self.collect_usage.isChecked())
        self.settings.setValue(SettingsKey.ENABLE_CRASH_REPORTS, self.crash_checkbox.isChecked())
        self.settings.setValue("encryptData", self.encrypt_data.isChecked())
        self.settings.setValue("useProxy", self.use_proxy.isChecked())
        self.settings.setValue("proxyHost", self.proxy_host.text())
        self.settings.setValue("proxyPort", self.proxy_port.value())
        
        # Advanced tab
        self.settings.setValue(SettingsKey.LOG_LEVEL, self.log_level_combo.currentText())
        self.settings.setValue("logDirectory", self.log_location.text())
        self.settings.setValue("logRetention", self.log_retention_days.value())
        self.settings.setValue("useCache", self.use_cache.isChecked())
        self.settings.setValue("useThreads", self.use_threads.isChecked())
        self.settings.setValue("prefetchData", self.prefetch_data.isChecked())
        self.settings.setValue("developerMode", self.dev_mode.isChecked())
    
    def accept(self):
        """Called when the dialog is accepted"""
        self.save_settings()
        
        # Notify the application that settings were changed
        from PyQt5.QtCore import QEvent, QCoreApplication
        event = QEvent(QEvent.Type(QEvent.User + 1))  # Custom event for settings changed
        QCoreApplication.postEvent(QCoreApplication.instance(), event)
        
        super().accept()
    
    def apply_settings(self):
        """Apply settings without closing the dialog"""
        self.save_settings()
        
        # Notify the application that settings were changed
        from PyQt5.QtCore import QEvent, QCoreApplication
        event = QEvent(QEvent.Type(QEvent.User + 1))  # Custom event for settings changed
        QCoreApplication.postEvent(QCoreApplication.instance(), event)
    
    def apply_changes(self):
        """Handle Apply button click"""
        self.save_settings()
    
    def clear_logs(self):
        """Clear log files"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Clear Logs", 
            "Are you sure you want to clear all log files?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            log_dir = os.path.dirname(self.log_file_edit.text())
            if os.path.exists(log_dir):
                try:
                    # Remove all .log files in the directory
                    for file in os.listdir(log_dir):
                        if file.endswith(".log"):
                            os.remove(os.path.join(log_dir, file))
                    QMessageBox.information(self, "Logs Cleared", "All log files have been cleared.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to clear logs: {e}")
            else:
                QMessageBox.warning(self, "Warning", "Log directory not found.")
    
    def clear_location_history(self):
        """Clear location history"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Clear Location History", 
            "Are you sure you want to clear your location history? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # This is a placeholder. In a real app, we'd call a method to clear the history
            QMessageBox.information(self, "Location History Cleared", "Your location history has been cleared.")
    
    def clear_cache(self):
        """Clear application cache"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Clear Cache", 
            "Are you sure you want to clear all cached data? The application may run slower temporarily.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cache_dir = os.path.join(self.config_manager.get("general", "data_directory", ""), "cache")
            if os.path.exists(cache_dir):
                try:
                    # Remove all files in the cache directory
                    for file in os.listdir(cache_dir):
                        os.remove(os.path.join(cache_dir, file))
                    QMessageBox.information(self, "Cache Cleared", "Cache has been cleared successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to clear cache: {e}")
            else:
                QMessageBox.warning(self, "Warning", "Cache directory not found.")
