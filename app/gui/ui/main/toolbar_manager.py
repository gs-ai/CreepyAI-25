"""
Toolbar Manager for CreepyAI
Manages creation and events for the toolbar
"""

import os
import logging
from typing import Dict, Any, Callable, Optional, List

from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QWidget, QMenu,
    QToolButton, QActionGroup, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence

from app.core.include.constants import ICON_SIZE
from app.core.path_utils import get_resource_path

logger = logging.getLogger(__name__)

class ToolbarManager:
    """
    Manages application toolbar creation and events
    
    Provides a consistent interface for creating and managing toolbar actions
    """
    
    def __init__(self, main_window: QMainWindow):
        """
        Initialize the toolbar manager
        
        Args:
            main_window: The main window to add toolbars to
        """
        self.main_window = main_window
        self.toolbars: Dict[str, QToolBar] = {}
        self.actions: Dict[str, QAction] = {}
        self.icon_size = QSize(ICON_SIZE, ICON_SIZE)
        
        # Default icon path
        self.icon_path = os.path.join("app", "resources", "icons")
    
    def create_main_toolbar(self) -> QToolBar:
        """
        Create and return the main toolbar
        
        Returns:
            The main toolbar
        """
        toolbar = QToolBar("Main Toolbar", self.main_window)
        toolbar.setIconSize(self.icon_size)
        self.main_window.addToolBar(toolbar)
        self.toolbars["main"] = toolbar
        
        return toolbar
    
    def create_map_toolbar(self) -> QToolBar:
        """
        Create and return the map toolbar
        
        Returns:
            The map toolbar
        """
        toolbar = QToolBar("Map Toolbar", self.main_window)
        toolbar.setIconSize(self.icon_size)
        self.main_window.addToolBar(toolbar)
        self.toolbars["map"] = toolbar
        
        return toolbar
    
    def create_plugin_toolbar(self) -> QToolBar:
        """
        Create and return the plugin toolbar
        
        Returns:
            The plugin toolbar
        """
        toolbar = QToolBar("Plugin Toolbar", self.main_window)
        toolbar.setIconSize(self.icon_size)
        self.main_window.addToolBar(toolbar)
        self.toolbars["plugin"] = toolbar
        
        return toolbar
    
    def add_action(self, 
                  toolbar_name: str, 
                  action_id: str,
                  text: str,
                  callback: Callable,
                  icon_name: Optional[str] = None,
                  status_tip: Optional[str] = None,
                  shortcut: Optional[str] = None,
                  checkable: bool = False) -> QAction:
        """
        Add an action to a toolbar
        
        Args:
            toolbar_name: Name of the toolbar to add to
            action_id: Unique identifier for the action
            text: Text for the action
            callback: Function to call when triggered
            icon_name: Name of the icon file
            status_tip: Status bar tip text
            shortcut: Keyboard shortcut
            checkable: Whether the action is checkable
        
        Returns:
            The created action
        """
        if toolbar_name not in self.toolbars:
            logger.warning(f"Toolbar '{toolbar_name}' not found")
            return None
        
        toolbar = self.toolbars[toolbar_name]
        
        # Create the action
        action = QAction(text, self.main_window)
        
        # Set icon if provided
        if icon_name:
            action.setIcon(self.get_icon(icon_name))
        
        # Set status tip if provided
        if status_tip:
            action.setStatusTip(status_tip)
        
        # Set shortcut if provided
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        # Set checkable if requested
        action.setCheckable(checkable)
        
        # Connect callback
        action.triggered.connect(callback)
        
        # Add to toolbar and store
        toolbar.addAction(action)
        self.actions[action_id] = action
        
        return action

    def add_separator(self, toolbar_name: str) -> None:
        """
        Add a separator to a toolbar
        
        Args:
            toolbar_name: Name of the toolbar to add to
        """
        if toolbar_name not in self.toolbars:
            logger.warning(f"Toolbar '{toolbar_name}' not found")
            return
        
        self.toolbars[toolbar_name].addSeparator()
    
    def add_widget(self, toolbar_name: str, widget: QWidget) -> None:
        """
        Add a widget to a toolbar
        
        Args:
            toolbar_name: Name of the toolbar to add to
            widget: Widget to add
        """
        if toolbar_name not in self.toolbars:
            logger.warning(f"Toolbar '{toolbar_name}' not found")
            return
        
        self.toolbars[toolbar_name].addWidget(widget)
    
    def add_menu_action(self,
                       toolbar_name: str,
                       action_id: str,
                       text: str,
                       menu_items: List[Dict[str, Any]],
                       icon_name: Optional[str] = None,
                       status_tip: Optional[str] = None) -> QToolButton:
        """
        Add an action with a dropdown menu to a toolbar
        
        Args:
            toolbar_name: Name of the toolbar to add to
            action_id: Unique identifier for the action
            text: Text for the action
            menu_items: List of dictionaries with menu item details
                Each dictionary should have: 
                    - 'id': unique identifier 
                    - 'text': display text
                    - 'callback': function to call
                    - 'icon_name': (optional) icon name
            icon_name: Name of the icon file
            status_tip: Status bar tip text
        
        Returns:
            The created tool button
        """
        if toolbar_name not in self.toolbars:
            logger.warning(f"Toolbar '{toolbar_name}' not found")
            return None
        
        toolbar = self.toolbars[toolbar_name]
        
        # Create menu
        menu = QMenu()
        
        # Add menu items
        for item in menu_items:
            item_action = QAction(item['text'], self.main_window)
            
            if 'icon_name' in item:
                item_action.setIcon(self.get_icon(item['icon_name']))
            
            item_action.triggered.connect(item['callback'])
            menu.addAction(item_action)
            
            # Store the action
            self.actions[f"{action_id}_{item['id']}"] = item_action
        
        # Create tool button
        tool_button = QToolButton()
        tool_button.setText(text)
        tool_button.setMenu(menu)
        tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        
        if icon_name:
            tool_button.setIcon(self.get_icon(icon_name))
        
        if status_tip:
            tool_button.setStatusTip(status_tip)
        
        # Default action triggers the first menu item
        if menu_items:
            tool_button.setDefaultAction(self.actions[f"{action_id}_{menu_items[0]['id']}"])
        
        # Add to toolbar
        toolbar.addWidget(tool_button)
        
        return tool_button
    
    def get_action(self, action_id: str) -> Optional[QAction]:
        """
        Get an action by its ID
        
        Args:
            action_id: ID of the action to get
            
        Returns:
            The action or None if not found
        """
        return self.actions.get(action_id)
    
    def enable_action(self, action_id: str, enable: bool = True) -> None:
        """
        Enable or disable an action
        
        Args:
            action_id: ID of the action to modify
            enable: True to enable, False to disable
        """
        action = self.get_action(action_id)
        if action:
            action.setEnabled(enable)
    
    def get_icon(self, icon_name: str) -> QIcon:
        """
        Get an icon with fallback to system icons if file not found
        
        Args:
            icon_name: Name of the icon file
            
        Returns:
            The icon
        """
        # If icon_name is a path, use it directly
        if os.path.exists(icon_name):
            return QIcon(icon_name)
            
        # Try to find icon in resources
        icon_path = ""
        if resource_path := get_resource_path(os.path.join("icons", icon_name)):
            icon_path = str(resource_path)
        else:
            # Try the direct path
            direct_path = os.path.join(self.icon_path, icon_name)
            if os.path.exists(direct_path):
                icon_path = direct_path
        
        # If icon file exists, use it
        if icon_path:
            return QIcon(icon_path)
        
        # Use system theme icon as fallback
        system_icon_name = icon_name.replace("-icon.png", "").replace("-", "_")
        system_icon = QIcon.fromTheme(system_icon_name)
        
        # If system icon doesn't exist, use a standard icon as fallback
        if system_icon.isNull():
            # Map of standard fallback icons
            fallbacks = {
                "new-project-icon.png": QStyle.SP_FileIcon,
                "open-icon.png": QStyle.SP_DirOpenIcon,
                "save-icon.png": QStyle.SP_DialogSaveButton,
                "export-icon.png": QStyle.SP_DialogSaveButton,
                "import-icon.png": QStyle.SP_DialogOpenButton,
                "help-icon.png": QStyle.SP_DialogHelpButton,
                "about-icon.png": QStyle.SP_MessageBoxInformation,
                "add-icon.png": QStyle.SP_FileDialogNewFolder,
                "remove-icon.png": QStyle.SP_TrashIcon,
                "settings-icon.png": QStyle.SP_FileDialogDetailedView,
                "refresh-icon.png": QStyle.SP_BrowserReload
            }
            
            # Get style from application
            style = QApplication.style()
            
            # Use appropriate standard icon or default
            if icon_name in fallbacks:
                return style.standardIcon(fallbacks[icon_name])
            else:
                return style.standardIcon(QStyle.SP_TitleBarMenuButton)
        
        return system_icon
