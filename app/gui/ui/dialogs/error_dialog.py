"""
Error Dialog for CreepyAI
Provides a consistent way to display errors to users
"""

import logging
import traceback
import sys
import platform
from typing import Optional, Union, Dict, Any, List

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QDialogButtonBox,
    QApplication, QStyle, QFrame, QTabWidget,
    QGridLayout, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from app.core.include.button_styles import ButtonStyles

logger = logging.getLogger(__name__)

class ErrorDialog(QDialog):
    """
    Dialog for displaying errors to users with detailed 
    information and options to copy or report the error.
    """
    
    # Signal emitted when user requests to report error
    errorReported = pyqtSignal(str, str, str)  # title, message, details
    
    def __init__(self, 
                parent=None, 
                title: str = "Error", 
                message: str = "An error occurred", 
                details: Optional[str] = None,
                exception: Optional[Exception] = None):
        """
        Initialize the error dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main error message
            details: Detailed error information
            exception: Exception object (will extract info if details not provided)
        """
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # If an exception is provided but no details, extract the exception info
        if exception and not details:
            details = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        self.title = title
        self.message = message
        self.details = details
        self.exception = exception
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Error icon and message at the top
        header_layout = QHBoxLayout()
        
        # Error icon
        icon_label = QLabel()
        error_icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
        icon_label.setPixmap(error_icon.pixmap(48, 48))
        header_layout.addWidget(icon_label)
        
        # Error message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        header_layout.addWidget(message_label, 1)  # Give stretch factor
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Create tab widget for different views of the error
        tabs = QTabWidget()
        
        # Details tab
        if self.details:
            details_tab = QWidget()
            details_layout = QVBoxLayout(details_tab)
            
            details_text = QTextEdit()
            details_text.setReadOnly(True)
            details_text.setPlainText(self.details)
            details_layout.addWidget(details_text)
            
            tabs.addTab(details_tab, "Details")
        
        # System info tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        system_info = self.get_system_info()
        system_text = QTextEdit()
        system_text.setReadOnly(True)
        
        # Format system info as text
        info_text = ""
        for key, value in system_info.items():
            info_text += f"{key}: {value}\n"
        
        system_text.setPlainText(info_text)
        system_layout.addWidget(system_text)
        
        tabs.addTab(system_tab, "System Information")
        
        layout.addWidget(tabs)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        # Copy button
        copy_button = QPushButton("Copy Details")
        copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        copy_button.clicked.connect(self.copy_to_clipboard)
        ButtonStyles.secondary_button(copy_button)
        button_layout.addWidget(copy_button)
        
        # Report button
        report_button = QPushButton("Report Error")
        report_button.setIcon(QIcon.fromTheme("dialog-information"))
        report_button.clicked.connect(self.report_error)
        ButtonStyles.secondary_button(report_button)
        button_layout.addWidget(report_button)
        
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setIcon(QIcon.fromTheme("window-close"))
        close_button.clicked.connect(self.accept)
        ButtonStyles.primary_button(close_button)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def copy_to_clipboard(self):
        """Copy error details to clipboard"""
        clipboard = QApplication.clipboard()
        
        # Format the text to include title, message and details
        text = f"{self.title}\n\n{self.message}"
        
        if self.details:
            text += f"\n\nDetails:\n{self.details}"
        
        # Add some system info
        system_info = self.get_system_info()
        text += "\n\nSystem Information:\n"
        for key, value in system_info.items():
            text += f"{key}: {value}\n"
        
        clipboard.setText(text)
        
        # Show feedback to user
        self.show_toast("Error details copied to clipboard")
    
    def report_error(self):
        """Report the error"""
        # Emit signal with error information
        self.errorReported.emit(self.title, self.message, self.details or "")
        self.show_toast("Error report sent")
    
    def show_toast(self, message: str):
        """Show a temporary message"""
        # This is a simple implementation; in a real app we might use a more sophisticated toast mechanism
        status_bar = self.parent().statusBar() if self.parent() and hasattr(self.parent(), 'statusBar') else None
        
        if status_bar:
            status_bar.showMessage(message, 3000)  # Show for 3 seconds
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        info = {
            "Platform": platform.platform(),
            "Python Version": sys.version.split()[0],
            "System": platform.system(),
            "Architecture": platform.architecture()[0],
            "Processor": platform.processor(),
        }
        
        # Add Qt version if available
        try:
            from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
            info["Qt Version"] = QT_VERSION_STR
            info["PyQt Version"] = PYQT_VERSION_STR
        except ImportError:
            pass
        
        return info
    
    @classmethod
    def show_error(cls, parent=None, title: str = "Error", message: str = "An error occurred", 
                  details: Optional[str] = None, exception: Optional[Exception] = None) -> 'ErrorDialog':
        """
        Static method to create, show and return an error dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main error message
            details: Detailed error information
            exception: Exception object
            
        Returns:
            The created dialog
        """
        dialog = cls(parent, title, message, details, exception)
        dialog.exec_()
        return dialog
    
    @classmethod
    def handle_exception(cls, parent=None, e: Exception, title: str = "Error", 
                        message: Optional[str] = None) -> 'ErrorDialog':
        """
        Handle an exception by showing an error dialog
        
        Args:
            parent: Parent widget
            e: Exception to handle
            title: Dialog title
            message: Main error message (default: exception's string representation)
            
        Returns:
            The created dialog
        """
        if message is None:
            message = str(e)
            
        # Log the error
        logger.error(f"{title}: {message}", exc_info=True)
        
        # Show the dialog
        return cls.show_error(parent, title, message, exception=e)
