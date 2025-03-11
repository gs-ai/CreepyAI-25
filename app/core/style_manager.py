"""
Style Manager for CreepyAI
Handles dynamic styling of UI elements, including dark mode support
"""

import os
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QApplication, QToolButton
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPalette, QColor

from app.core.include.constants import APP_RESOURCES_DIR
from app.core.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)

class ComponentStyle(Enum):
    """Style types for UI components"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"
    TEXT = "text"
    LINK = "link"
    DISABLED = "disabled"

class StyleManager(QObject):
    """
    Manages dynamic styling of UI components
    
    Coordinates with ThemeManager to apply appropriate styles based on current theme
    """
    
    styleChanged = pyqtSignal()
    
    def __init__(self, theme_manager: Optional[ThemeManager] = None):
        """
        Initialize the style manager
        
        Args:
            theme_manager: Optional ThemeManager instance to use. 
                         If None, a new one will be created.
        """
        super().__init__()
        
        # Create or use provided theme manager
        self._theme_manager = theme_manager or ThemeManager()
        
        # Connect to theme changes
        self._theme_manager.themeChanged.connect(self._on_theme_changed)
        
        # Load style definitions
        self._styles = self._load_styles()
        
        # Components to update on style changes
        self._managed_components: Dict[int, Dict[str, Any]] = {}
        
        logger.debug("Style manager initialized")
    
    def _load_styles(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Load style definitions for different themes"""
        # Default styles for light and dark themes
        styles = {
            'light': {
                ComponentStyle.PRIMARY.value: {
                    'background': '#4a86e8',
                    'color': '#ffffff',
                    'border': 'none',
                    'hover-background': '#5c94f0',
                    'hover-color': '#ffffff',
                    'pressed-background': '#3b77d9',
                    'pressed-color': '#ffffff',
                },
                ComponentStyle.SECONDARY.value: {
                    'background': '#f5f5f5',
                    'color': '#333333',
                    'border': '1px solid #cccccc',
                    'hover-background': '#e5e5e5',
                    'hover-color': '#333333',
                    'pressed-background': '#d0d0d0',
                    'pressed-color': '#333333',
                },
                # ... other styles from previous implementation ...
            },
            'dark': {
                ComponentStyle.PRIMARY.value: {
                    'background': '#4a86e8',
                    'color': '#ffffff',
                    'border': 'none',
                    'hover-background': '#5c94f0',
                    'hover-color': '#ffffff',
                    'pressed-background': '#3b77d9',
                    'pressed-color': '#ffffff',
                },
                ComponentStyle.SECONDARY.value: {
                    'background': '#3a3a3a',
                    'color': '#e0e0e0',
                    'border': '1px solid #555555',
                    'hover-background': '#444444',
                    'hover-color': '#e0e0e0',
                    'pressed-background': '#2a2a2a',
                    'pressed-color': '#e0e0e0',
                },
                # ... other styles from previous implementation ...
            }
        }
        
        return styles
    
    def _on_theme_changed(self, theme: Theme) -> None:
        """
        Handle theme change event
        
        Args:
            theme: New theme
        """
        logger.debug(f"Theme changed to {theme.value}, updating managed components")
        self.update_all_components()
        self.styleChanged.emit()
    
    def get_current_theme_mode(self) -> str:
        """
        Get the current theme mode (light or dark)
        
        Returns:
            'light' or 'dark'
        """
        theme = self._theme_manager.get_current_theme()
        
        # If system theme, determine which mode is active
        if theme == Theme.SYSTEM:
            # Get background color and determine if it's dark based on brightness
            app = QApplication.instance()
            bg_color = app.palette().color(QPalette.Window)
            brightness = bg_color.red() * 0.299 + bg_color.green() * 0.587 + bg_color.blue() * 0.114
            return 'dark' if brightness < 128 else 'light'
        
        return 'dark' if theme == Theme.DARK else 'light'
    
    def register_component(self, component: QWidget, style_type: ComponentStyle) -> None:
        """
        Register a component for style management
        
        Args:
            component: Widget to style
            style_type: Type of style to apply
        """
        # Store component info using object ID as key
        component_id = id(component)
        self._managed_components[component_id] = {
            'component': component,
            'style_type': style_type
        }
        
        # Apply initial style
        self.apply_style(component, style_type)
    
    def unregister_component(self, component: QWidget) -> None:
        """
        Remove a component from style management
        
        Args:
            component: Widget to remove
        """
        component_id = id(component)
        if component_id in self._managed_components:
            del self._managed_components[component_id]
    
    def apply_style(self, component: QWidget, style_type: ComponentStyle) -> None:
        """
        Apply a style to a component
        
        Args:
            component: Widget to style
            style_type: Type of style to apply
        """
        # Get current theme mode (light or dark)
        theme_mode = self.get_current_theme_mode()
        
        # Get style definition for this type and theme
        style_def = self._styles[theme_mode].get(style_type.value, {})
        
        if not style_def:
            logger.warning(f"No style definition found for {style_type.value} in {theme_mode} mode")
            return
        
        # Apply style based on widget type
        if isinstance(component, QPushButton):
            self._apply_button_style(component, style_def)
        elif isinstance(component, QLabel):
            self._apply_label_style(component, style_def)
        elif isinstance(component, QToolButton):
            self._apply_tool_button_style(component, style_def)
        else:
            # For other widget types, use generic styling
            self._apply_generic_style(component, style_def)
            
    def _apply_button_style(self, button: QPushButton, style_def: Dict[str, str]) -> None:
        """
        Apply style to a QPushButton
        
        Args:
            button: Button to style
            style_def: Style definition dictionary
        """
        # Create CSS style string for the button
        css = f"""
            QPushButton {{
                background-color: {style_def.get('background', '#f5f5f5')};
                color: {style_def.get('color', '#333333')};
                border: {style_def.get('border', '1px solid #cccccc')};
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {style_def.get('hover-background', '#e5e5e5')};
                color: {style_def.get('hover-color', '#333333')};
            }}
            QPushButton:pressed {{
                background-color: {style_def.get('pressed-background', '#d0d0d0')};
                color: {style_def.get('pressed-color', '#333333')};
            }}
            QPushButton:disabled {{
                background-color: {style_def.get('disabled-background', '#cccccc')};
                color: {style_def.get('disabled-color', '#888888')};
                border: {style_def.get('disabled-border', '1px solid #dddddd')};
            }}
        """
        
        button.setStyleSheet(css)
        button.setCursor(Qt.PointingHandCursor)
        
    def _apply_label_style(self, label: QLabel, style_def: Dict[str, str]) -> None:
        """
        Apply style to a QLabel
        
        Args:
            label: Label to style
            style_def: Style definition dictionary
        """
        # Create CSS style string for the label
        css = f"""
            QLabel {{
                color: {style_def.get('color', '#333333')};
                background-color: {style_def.get('background', 'transparent')};
                border: {style_def.get('border', 'none')};
                padding: 2px;
            }}
        """
        
        label.setStyleSheet(css)
        
    def _apply_tool_button_style(self, button: QToolButton, style_def: Dict[str, str]) -> None:
        """
        Apply style to a QToolButton
        
        Args:
            button: Button to style
            style_def: Style definition dictionary
        """
        # Create CSS style string for the tool button
        css = f"""
            QToolButton {{
                background-color: {style_def.get('background', '#f5f5f5')};
                color: {style_def.get('color', '#333333')};
                border: {style_def.get('border', '1px solid #cccccc')};
                padding: 4px 8px;
                border-radius: 3px;
            }}
            QToolButton:hover {{
                background-color: {style_def.get('hover-background', '#e5e5e5')};
                color: {style_def.get('hover-color', '#333333')};
                border-color: {style_def.get('hover-border-color', '#999999')};
            }}
            QToolButton:pressed {{
                background-color: {style_def.get('pressed-background', '#d0d0d0')};
                color: {style_def.get('pressed-color', '#333333')};
            }}
            QToolButton:disabled {{
                background-color: {style_def.get('disabled-background', '#cccccc')};
                color: {style_def.get('disabled-color', '#888888')};
                border: {style_def.get('disabled-border', '1px solid #dddddd')};
            }}
            QToolButton::menu-button {{
                width: 16px;
                border-left: {style_def.get('border', '1px solid #cccccc')};
            }}
        """
        
        button.setStyleSheet(css)
        button.setCursor(Qt.PointingHandCursor)
        
    def _apply_generic_style(self, widget: QWidget, style_def: Dict[str, str]) -> None:
        """
        Apply a generic style to any widget
        
        Args:
            widget: Widget to style
            style_def: Style definition dictionary
        """
        # Get the widget's class name
        widget_class = widget.__class__.__name__
        
        # Create CSS style string for the widget
        css = f"""
            {widget_class} {{
                background-color: {style_def.get('background', 'transparent')};
                color: {style_def.get('color', '#333333')};
                border: {style_def.get('border', 'none')};
            }}
        """
        
        widget.setStyleSheet(css)
    
    def update_all_components(self) -> None:
        """Update all registered components with current theme styles"""
        for component_id, component_info in self._managed_components.items():
            component = component_info['component']
            style_type = component_info['style_type']
            
            # Check if component still exists
            if component:
                try:
                    self.apply_style(component, style_type)
                except Exception as e:
                    logger.error(f"Error updating component style: {e}")
            else:
                # Remove stale reference
                del self._managed_components[component_id]
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color value for the current theme
        
        Args:
            color_name: Color name (e.g., 'primary', 'background')
            
        Returns:
            Color value as hex string
        """
        # Pass through to theme manager
        return self._theme_manager.get_color(color_name)
    
    def set_theme(self, theme: Theme) -> None:
        """
        Set the application theme
        
        Args:
            theme: Theme to apply
        """
        self._theme_manager.set_theme(theme)
        # The theme change signal handler will update components

    def toggle_theme(self) -> Theme:
        """
        Toggle between light and dark themes
        
        Returns:
            The new theme
        """
        current_theme = self._theme_manager.get_current_theme()
        
        # If system theme, detect the current mode to toggle from
        if current_theme == Theme.SYSTEM:
            theme_mode = self.get_current_theme_mode()
            current_theme = Theme.DARK if theme_mode == 'dark' else Theme.LIGHT
        
        # Toggle theme
        new_theme = Theme.LIGHT if current_theme == Theme.DARK else Theme.DARK
        self._theme_manager.set_theme(new_theme)
        
        return new_theme
