    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Error handling utilities for the CreepyAI application.
"""

import sys
import traceback
import logging
import os
import datetime
from functools import wraps
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger('CreepyAI.ErrorHandler')

class ErrorHandler:
    """Class for handling errors in the application"""
    
    @staticmethod
    def get_error_log_path():
        """Get the path to the error log file"""
        # Use the user's home directory
        from pathlib import Path
        error_log_dir = os.path.join(str(Path.home()), '.creepyai', 'logs')
        
        # Create directory if it doesn't exist
        if not os.path.exists(error_log_dir):
            os.makedirs(error_log_dir)
        
        # Use a datestamped filename
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return os.path.join(error_log_dir, f'creepyai_errors_{today}.log')
    
    @staticmethod
    def setup_error_logging():
        """Set up logging for errors"""
        error_log_path = ErrorHandler.get_error_log_path()
        
        # Create file handler for error logging
        file_handler = logging.FileHandler(error_log_path)
        file_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to the root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        logger.info(f"Error logging set up. Errors will be logged to {error_log_path}")
    
    @staticmethod
    def log_exception(e, context=None):
        """Log an exception with optional context information"""
        context_str = f" in {context}" if context else ""
        logger.error(f"Exception{context_str}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a formatted error string that can be shown to the user
        error_details = str(e)
        return error_details
    
    @staticmethod
    def show_error_dialog(parent, title, message, detailed_text=None):
        """Show an error dialog to the user"""
        error_box = QMessageBox(parent)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        
        if detailed_text:
            error_box.setDetailedText(detailed_text)
        
        error_box.addButton(QMessageBox.Ok)
        error_box.exec_()
    
    @staticmethod
    def ui_exception_handler(parent=None):
        """
        Decorator for handling exceptions in UI methods
        
        Example usage:
        @ErrorHandler.ui_exception_handler()
        def some_method(self, arg1, arg2):
            # Method code that might raise exceptions
        """
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    # Log the exception
                    error_details = ErrorHandler.log_exception(e, func.__name__)
                    
                    # Show error dialog
                    parent_widget = parent if parent is not None else self
                    ErrorHandler.show_error_dialog(
                        parent_widget,
                        "Error",
                        f"An error occurred in {func.__name__}",
                        detailed_text=error_details
                    )
            return wrapper
        return decorator

def install_global_exception_handler():
    """Install a global exception handler for unhandled exceptions"""
    def global_exception_handler(exctype, value, tb):
        """Handle uncaught exceptions"""
        # Log the exception
        logger.critical("Uncaught exception", exc_info=(exctype, value, tb))
        
        # Format traceback for display
        traceback_text = ''.join(traceback.format_exception(exctype, value, tb))
        
        # Show error dialog
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            if QApplication.instance():
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setWindowTitle("Critical Error")
                error_box.setText("An unexpected error occurred. The application may be unstable.")
                error_box.setDetailedText(traceback_text)
                error_box.addButton(QMessageBox.Ok)
                error_box.exec_()
        except:
            # If showing the dialog fails, just print the error
            print("CRITICAL ERROR:", file=sys.stderr)
            print(traceback_text, file=sys.stderr)
    
    # Install the handler
    sys.excepthook = global_exception_handler

import json
import hashlib

class ErrorTracker:
    """Class for tracking and reporting errors in CreepyAI."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorTracker, cls).__new__(cls)
            cls._instance.errors = []
            cls._instance.warnings = []
            cls._instance.dependency_errors = []
        return cls._instance
    
    def track_error(self, module_name, function_name, error_msg, stack_trace=None):
        """Track a general error."""
        error_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'module': module_name,
            'function': function_name,
            'message': error_msg,
            'stack_trace': stack_trace or traceback.format_exc()
        }
        self.errors.append(error_data)
        logger.error(f"Error in {module_name}.{function_name}: {error_msg}")
        return error_data
    
    def track_warning(self, module_name, warning_msg):
        """Track a warning."""
        warning_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'module': module_name,
            'message': warning_msg
        }
        self.warnings.append(warning_data)
        logger.warning(f"Warning in {module_name}: {warning_msg}")
        return warning_data
    
    def track_dependency_error(self, module_name, feature_name, error_message):
        """Track a dependency-related error."""
        dep_error = {
            'timestamp': datetime.datetime.now().isoformat(),
            'module': module_name,
            'feature': feature_name,
            'message': error_message
        }
        self.dependency_errors.append(dep_error)
        logger.error(f"Dependency error for {feature_name} in {module_name}: {error_message}")
        return dep_error
    
    def get_recent_errors(self, count=10):
        """Get the most recent errors."""
        return sorted(self.errors, key=lambda x: x['timestamp'], reverse=True)[:count]
    
    def get_recent_warnings(self, count=10):
        """Get the most recent warnings."""
        return sorted(self.warnings, key=lambda x: x['timestamp'], reverse=True)[:count]
    
    def has_errors(self):
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_dependency_errors(self):
        """Check if there are any dependency errors."""
        return len(self.dependency_errors) > 0
    
    def get_dependency_issues(self):
        """Get all dependency issues."""
        return self.dependency_errors
    
    def clear_errors(self):
        """Clear all tracked errors."""
        self.errors = []
        self.warnings = []
    
    def get_error_summary(self):
        """Get a summary of all errors."""
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'dependency_error_count': len(self.dependency_errors),
            'recent_errors': self.get_recent_errors(5)
        }