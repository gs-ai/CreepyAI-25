"""
Button Style Utilities for CreepyAI
Provides consistent button styling across the application
"""

import logging
from typing import Optional, Union

from PyQt5.QtWidgets import QPushButton, QToolButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

logger = logging.getLogger(__name__)

class ButtonStyles:
    """Static class providing methods to style buttons consistently"""
    
    @staticmethod
    def primary_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply primary button style (blue, emphasized)
        
        Args:
            button: Button to style
        """
        button.setProperty("primary", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #5c94f0;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #3b77d9;
            }
            QPushButton:disabled, QToolButton:disabled {
                background-color: #a3bceb;
                color: #e1e1e1;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)

    @staticmethod
    def secondary_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply secondary button style (light gray)
        
        Args:
            button: Button to style
        """
        button.setProperty("secondary", True)
        stylesheet = """
            QPushButton, QToolButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #e5e5e5;
                border-color: #999999;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #d0d0d0;
                border-color: #777777;
            }
            QPushButton:disabled, QToolButton:disabled {
                background-color: #f8f8f8;
                color: #aaaaaa;
                border-color: #dddddd;
            }
        """
        button.setStyleSheet(stylesheet)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def danger_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply danger/warning button style (red)
        
        Args:
            button: Button to style
        """
        button.setProperty("danger", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #e04050;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #c82333;
            }
            QPushButton:disabled, QToolButton:disabled {
                background-color: #e6a0a7;
                color: #e1e1e1;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def success_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply success button style (green)
        
        Args:
            button: Button to style
        """
        button.setProperty("success", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #34b354;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #218838;
            }
            QPushButton:disabled, QToolButton:disabled {
                background-color: #94d3a2;
                color: #e1e1e1;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def info_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply info button style (light blue)
        
        Args:
            button: Button to style
        """
        button.setProperty("info", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #117a8b;
            }
            QPushButton:disabled, QToolButton:disabled {
                background-color: #8bd1df;
                color: #e1e1e1;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def warning_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply warning button style (yellow)
        
        Args:
            button: Button to style
        """
        button.setProperty("warning", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: #ffc107;
                color: #333333;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #ffca2c;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #e0a800;
            }
            QPushButton:disabled, QToolButton:disabled {
                background-color: #ffe083;
                color: #777777;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def text_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply text button style (no background, just text)
        
        Args:
            button: Button to style
        """
        button.setProperty("text", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: transparent;
                color: #4a86e8;
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover, QToolButton:hover {
                color: #5c94f0;
            }
            QPushButton:pressed, QToolButton:pressed {
                color: #3b77d9;
            }
            QPushButton:disabled, QToolButton:disabled {
                color: #a3bceb;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def link_button(button: Union[QPushButton, QToolButton]) -> None:
        """
        Apply link button style (looks like a hyperlink)
        
        Args:
            button: Button to style
        """
        button.setProperty("link", True)
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: transparent;
                color: #4a86e8;
                border: none;
                text-decoration: underline;
                padding: 4px;
            }
            QPushButton:hover, QToolButton:hover {
                color: #5c94f0;
            }
            QPushButton:pressed, QToolButton:pressed {
                color: #3b77d9;
            }
            QPushButton:disabled, QToolButton:disabled {
                color: #a3bceb;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def icon_button(button: Union[QPushButton, QToolButton], icon_path: str, size: int = 24) -> None:
        """
        Set up a button with just an icon
        
        Args:
            button: Button to style
            icon_path: Path to the icon file
            size: Size of the icon in pixels
        """
        button.setIcon(QIcon(icon_path))
        button.setIconSize(Qt.QSize(size, size))
        button.setText("")
        button.setFixedSize(size + 12, size + 12)  # Add some padding
        button.setStyleSheet("""
            QPushButton, QToolButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 3px;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 3px;
            }
            QPushButton:disabled, QToolButton:disabled {
                opacity: 0.5;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)
    
    @staticmethod
    def apply_dark_mode(button: Union[QPushButton, QToolButton]) -> None:
        """
        Adjust button styles for dark mode
        
        Args:
            button: Button to style
        """
        if button.property("secondary"):
            button.setStyleSheet("""
                QPushButton, QToolButton {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font-weight: 500;
                }
                QPushButton:hover, QToolButton:hover {
                    background-color: #444444;
                    border-color: #666666;
                }
                QPushButton:pressed, QToolButton:pressed {
                    background-color: #2a2a2a;
                    border-color: #777777;
                }
                QPushButton:disabled, QToolButton:disabled {
                    background-color: #2a2a2a;
                    color: #707070;
                    border-color: #333333;
                }
            """)
