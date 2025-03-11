"""
Theme Manager for CreepyAI
Handles light/dark mode and theme preferences
"""

import os
import logging
import enum
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from PyQt5.QtGui import QPalette, QColor

logger = logging.getLogger(__name__)

class Theme(enum.Enum):
    """Theme options for the application"""
    SYSTEM = "system"  # Follow system theme
    LIGHT = "light"    # Light theme
    DARK = "dark"      # Dark theme


class ThemeManager(QObject):
    """
    Manages application theming and appearance
    
    Handles loading theme stylesheets, switching between light and dark mode,
    and applying consistent colors throughout the application.
    """
    
    # Signal emitted when theme changes
    themeChanged = pyqtSignal(Theme)
    
    def __init__(self):
        super().__init__()
        self._current_theme = Theme.SYSTEM
        self._app = QApplication.instance()
        self._original_palette = self._app.palette()
        self._style_sheets = {
            Theme.LIGHT: "",  # Default Qt style
            Theme.DARK: self._load_style_sheet("app/core/include/style_dark.qss")
        }
        
        # Theme colors for programmatic use
        self._colors = {
            Theme.LIGHT: {
                "background": "#f8f8f8",
                "foreground": "#333333",
                "primary": "#4a86e8",
                "secondary": "#f5f5f5",
                "accent": "#4a86e8",
                "error": "#dc3545",
                "warning": "#ffc107",
                "success": "#28a745"
            },
            Theme.DARK: {
                "background": "#2d2d2d",
                "foreground": "#e0e0e0",
                "primary": "#4a86e8",
                "secondary": "#3a3a3a",
                "accent": "#5c94f0",
                "error": "#e04050",
                "warning": "#ffd350",
                "success": "#48c774"
            }
        }
        
        # Load saved theme preference
        self._settings = QSettings("CreepyAI", "Application")
        saved_theme = self._settings.value("theme", Theme.SYSTEM.value)
        
        # Set initial theme
        for theme in Theme:
            if theme.value == saved_theme:
                self._current_theme = theme
                break
        
        # Apply initial theme
        self.apply_theme()
    
    def _load_style_sheet(self, path: str) -> str:
        """Load a stylesheet from file"""
        try:
            if not os.path.exists(path):
                logger.warning(f"Stylesheet not found: {path}")
                return ""
                
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Failed to load stylesheet {path}: {e}")
            return ""
    
    def get_current_theme(self) -> Theme:
        """Get the current theme setting"""
        return self._current_theme
    
    def set_theme(self, theme: Theme) -> None:
        """
        Set application theme
        
        Args:
            theme: The theme to apply
        """
        if theme != self._current_theme:
            self._current_theme = theme
            self.apply_theme()
            
            # Save theme preference
            self._settings.setValue("theme", theme.value)
            
            # Emit theme changed signal
            self.themeChanged.emit(theme)
    
    def apply_theme(self) -> None:
        """Apply the current theme to the application"""
        theme_to_apply = self._current_theme
        
        # If system theme, detect if we should use dark or light
        if theme_to_apply == Theme.SYSTEM:
            # Detect system theme
            # This is a simplified detection - in reality you'd use platform-specific methods
            system_palette = self._app.palette()
            bg_color = system_palette.color(QPalette.Window)
            brightness = bg_color.red() * 0.299 + bg_color.green() * 0.587 + bg_color.blue() * 0.114
            
            # If dark background, use dark theme
            if brightness < 128:
                theme_to_apply = Theme.DARK
            else:
                theme_to_apply = Theme.LIGHT
        
        # Apply stylesheet
        self._app.setStyleSheet(self._style_sheets[theme_to_apply])
        
        # Apply palette customizations for the theme
        if theme_to_apply == Theme.DARK:
            self._apply_dark_palette()
        else:
            # Restore original palette for light theme
            self._app.setPalette(self._original_palette)
    
    def _apply_dark_palette(self) -> None:
        """Apply dark mode palette customizations"""
        palette = QPalette(self._original_palette)
        
        # Set dark theme colors
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
        palette.setColor(QPalette.Base, QColor(36, 36, 36))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
        palette.setColor(QPalette.Text, QColor(224, 224, 224))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(74, 134, 232))
        palette.setColor(QPalette.Highlight, QColor(74, 134, 232))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Apply palette
        self._app.setPalette(palette)
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color value for the current theme
        
        Args:
            color_name: Name of the color to retrieve (e.g., "background", "primary")
            
        Returns:
            Color value as hex string (e.g., "#4a86e8")
        """
        theme = self._current_theme
        
        # If system theme, determine which color set to use
        if theme == Theme.SYSTEM:
            # Same check as in apply_theme()
            system_palette = self._app.palette()
            bg_color = system_palette.color(QPalette.Window)
            brightness = bg_color.red() * 0.299 + bg_color.green() * 0.587 + bg_color.blue() * 0.114
            
            theme = Theme.DARK if brightness < 128 else Theme.LIGHT
        
        # Return the requested color for the theme
        return self._colors[theme].get(color_name, "#000000")
