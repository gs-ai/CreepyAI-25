"""
Plugin browser widget for CreepyAI
"""
import os
import sys
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QTextEdit, QFrame, QSplitter,
    QCheckBox, QComboBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont

try:
    from app.gui.resources.icons.plugin_icons import get_plugin_icon
except ImportError:
    # Default function if we can't import the module
    def get_plugin_icon(plugin_name, category):
        return QIcon()

logger = logging.getLogger(__name__)

class PluginBrowserWidget(QWidget):
    """
    A widget for browsing and interacting with plugins
    """
    pluginSelected = pyqtSignal(str) # Emitted when a plugin is selected
    pluginRun = pyqtSignal(str)      # Emitted when a plugin is run
    pluginConfigure = pyqtSignal(str) # Emitted when a plugin is configured
    
    def __init__(self, parent=None):
        super(PluginBrowserWidget, self).__init__(parent)
        
        # Plugin manager (to be set later)
        self.plugin_manager = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Create splitter for list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Plugin list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        list_layout.addWidget(self.category_combo)
        
        # Plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.setMinimumWidth(200)
        list_layout.addWidget(self.plugin_list)
        
        # Right side - Plugin details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Plugin info
        info_group = QGroupBox("Plugin Information")
        info_layout = QFormLayout(info_group)
        
        self.plugin_name_label = QLabel("")
        self.plugin_version_label = QLabel("")
        self.plugin_author_label = QLabel("")
        self.plugin_category_label = QLabel("")
        
        info_layout.addRow("Name:", self.plugin_name_label)
        info_layout.addRow("Version:", self.plugin_version_label)
        info_layout.addRow("Author:", self.plugin_author_label)
        info_layout.addRow("Category:", self.plugin_category_label)
        
        details_layout.addWidget(info_group)
        
        # Plugin description
        description_group = QGroupBox("Description")
        description_layout = QVBoxLayout(description_group)
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        description_layout.addWidget(self.description_text)
        
        details_layout.addWidget(description_group)
        
        # Plugin actions
        actions_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.configure_button = QPushButton("Configure")
        
        actions_layout.addWidget(self.run_button)
        actions_layout.addWidget(self.configure_button)
        
        details_layout.addLayout(actions_layout)
        
        # Add widgets to splitter
        splitter.addWidget(list_widget)
        splitter.addWidget(details_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 400])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Connect signals
        self.plugin_list.currentItemChanged.connect(self.on_plugin_selected)
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        self.run_button.clicked.connect(self.on_run_clicked)
        self.configure_button.clicked.connect(self.on_configure_clicked)
        
        # Initially disable buttons
        self.run_button.setEnabled(False)
        self.configure_button.setEnabled(False)
        
    def set_plugin_manager(self, plugin_manager):
        """
        Set the plugin manager and populate the list
        
        Args:
            plugin_manager: PluginManager instance
        """
        self.plugin_manager = plugin_manager
        self.populate_plugin_list()
        self.populate_categories()
        
    def populate_categories(self):
        """
        Populate the category filter combobox
        """
        if not self.plugin_manager:
            return
            
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        
        categories = self.plugin_manager.get_categories()
        for category in sorted(categories):
            self.category_combo.addItem(category.title())
            
    def populate_plugin_list(self):
        """
        Populate the plugin list with available plugins
        """
        if not self.plugin_manager:
            return
            
        self.plugin_list.clear()
        
        plugins = self.plugin_manager.get_all_plugins()
        
        # Group plugins by category
        by_category = {}
        for name, plugin in plugins.items():
            category = self.plugin_manager.get_category(name)
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((name, plugin))
        
        # Add plugins by category
        for category in sorted(by_category.keys()):
            # Add category header item
            category_item = QListWidgetItem(f"== {category.upper()} ==")
            category_item.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable
            font = category_item.font()
            font.setBold(True)
            category_item.setFont(font)
            self.plugin_list.addItem(category_item)
            
            # Add plugins in this category
            for name, plugin in sorted(by_category[category]):
                # Create list widget item
                item = QListWidgetItem(f"  {name}")
                item.setData(Qt.UserRole, name)  # Store actual plugin name
                
                # Set icon based on category and plugin name
                icon = get_plugin_icon(name, category)
                item.setIcon(icon)
                
                # Add plugin info as tooltip
                if hasattr(plugin, 'get_info'):
                    info = plugin.get_info()
                    tooltip = f"{info.get('name', name)} v{info.get('version', '1.0')}\n"
                    tooltip += f"Category: {category}\n"
                    tooltip += f"Author: {info.get('author', 'Unknown')}\n"
                    tooltip += f"Description: {info.get('description', 'No description')}"
                    item.setToolTip(tooltip)
                
                # Add to list widget
                self.plugin_list.addItem(item)
                
    def filter_by_category(self, category_text):
        """
        Filter plugins by category
        
        Args:
            category_text: Category to filter by
        """
        if not self.plugin_manager:
            return
            
        # Show all plugins if "All Categories" is selected
        if category_text == "All Categories":
            self.populate_plugin_list()
            return
            
        # Convert title case to lowercase
        category = category_text.lower()
        
        self.plugin_list.clear()
        
        plugins = self.plugin_manager.get_plugins_by_category(category)
        
        # Add plugins in this category
        for name, plugin in sorted(plugins.items()):
            # Create list widget item
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)  # Store actual plugin name
            
            # Set icon based on category and plugin name
            icon = get_plugin_icon(name, category)
            item.setIcon(icon)
            
            # Add plugin info as tooltip
            if hasattr(plugin, 'get_info'):
                info = plugin.get_info()
                tooltip = f"{info.get('name', name)} v{info.get('version', '1.0')}\n"
                tooltip += f"Category: {category}\n"
                tooltip += f"Author: {info.get('author', 'Unknown')}\n"
                tooltip += f"Description: {info.get('description', 'No description')}"
                item.setToolTip(tooltip)
            
            # Add to list widget
            self.plugin_list.addItem(item)
            
    def on_plugin_selected(self, current, previous):
        """
        Handle plugin selection change
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if not current or not self.plugin_manager:
            # Disable buttons if no item is selected
            self.run_button.setEnabled(False)
            self.configure_button.setEnabled(False)
            return
            
        # Get plugin name from item data
        plugin_name = current.data(Qt.UserRole)
        
        # It might be a category header (None data)
        if not plugin_name:
            # Disable buttons for category headers
            self.run_button.setEnabled(False)
            self.configure_button.setEnabled(False)
            
            # Clear plugin details
            self.plugin_name_label.setText("")
            self.plugin_version_label.setText("")
            self.plugin_author_label.setText("")
            self.plugin_category_label.setText("")
            self.description_text.setText("")
            return
            
        # Get plugin instance
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            return
        
        # Enable buttons
        self.run_button.setEnabled(True)
        self.configure_button.setEnabled(hasattr(plugin, 'configure'))
        
        # Update plugin details
        if hasattr(plugin, 'get_info'):
            info = plugin.get_info()
            self.plugin_name_label.setText(info.get('name', plugin_name))
            self.plugin_version_label.setText(info.get('version', '1.0.0'))
            self.plugin_author_label.setText(info.get('author', 'Unknown'))
            self.plugin_category_label.setText(self.plugin_manager.get_category(plugin_name).title())
            self.description_text.setText(info.get('description', 'No description available.'))
        
        # Emit signal
        self.pluginSelected.emit(plugin_name)
        
    def on_run_clicked(self):
        """
        Handle run button click
        """
        current_item = self.plugin_list.currentItem()
        if not current_item:
            return
            
        plugin_name = current_item.data(Qt.UserRole)
        if plugin_name:
            # Get plugin info
            plugin = self.plugin_manager.get_plugin(plugin_name)
            plugin_category = self.plugin_manager.get_category(plugin_name) if self.plugin_manager else "unknown"
            
            # Indicate that the plugin is running
            self.description_text.append("\nRunning plugin...")
            
            # Emit signal to run the plugin
            self.pluginRun.emit(plugin_name)
            
            # Note: actual plugin execution and results display is handled by the main window
            
    def on_configure_clicked(self):
        """
        Handle configure button click
        """
        current_item = self.plugin_list.currentItem()
        if not current_item:
            return
            
        plugin_name = current_item.data(Qt.UserRole)
        if plugin_name:
            self.pluginConfigure.emit(plugin_name)
