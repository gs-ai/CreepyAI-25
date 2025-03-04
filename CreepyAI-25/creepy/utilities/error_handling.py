#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import traceback
import json
import datetime
import logging
from functools import wraps

# Set up logging for error handling
error_logger = logging.getLogger('error_tracker')
error_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(), 'error_tracker.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
error_logger.addHandler(fh)

class ErrorTracker:
    """Class to track and manage errors throughout the application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorTracker, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the error tracker"""
        self.errors = {}
        self.error_count = 0
        self.report_file = os.path.join(os.getcwd(), 'creepy_error_report.json')
        self.load_existing_errors()
    
    def track_error(self, error_type, message, context=None):
        """Track a new error occurrence"""
        # Create a unique key for this error
        error_type_str = error_type.__name__ if hasattr(error_type, '__name__') else str(error_type)
        error_key = f"{error_type_str}_{message}"
        
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update existing error entry or create a new one
        if error_key in self.errors:
            self.errors[error_key]['count'] += 1
            self.errors[error_key]['last_seen'] = now
            if context and context not in self.errors[error_key]['contexts']:
                self.errors[error_key]['contexts'].append(context)
        else:
            self.errors[error_key] = {
                'type': error_type_str,
                'message': message,
                'count': 1,
                'first_seen': now,
                'last_seen': now,
                'contexts': [context] if context else []
            }
        
        self.error_count += 1
        error_logger.error(f"{error_type_str}: {message} (Context: {context})")
        
        # Save errors periodically
        if self.error_count % 10 == 0:  # Save every 10 errors
            self.save_error_report()
            
    def load_existing_errors(self):
        """Load errors from saved report file"""
        if os.path.exists(self.report_file):
            try:
                with open(self.report_file, 'r') as f:
                    data = json.load(f)
                    self.errors = data.get('errors', {})
                    self.error_count = data.get('total_count', 0)
            except Exception as e:
                error_logger.error(f"Failed to load error report: {e}")
                
    def save_error_report(self, filepath=None):
        """Save error report to file"""
        filepath = filepath or self.report_file
        try:
            report = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_count': self.error_count,
                'unique_count': len(self.errors),
                'errors': self.errors
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=4)
                
            return True
        except Exception as e:
            error_logger.error(f"Failed to save error report: {e}")
            return False
            
    def get_error_summary(self):
        """Get a summary of tracked errors"""
        return {
            'total_count': self.error_count,
            'unique_count': len(self.errors),
            'top_errors': sorted(
                self.errors.items(), 
                key=lambda x: x[1]['count'], 
                reverse=True
            )[:10]  # Top 10 errors
        }
        
    def clear(self):
        """Clear all tracked errors"""
        self.errors = {}
        self.error_count = 0
        
        # Save the empty state
        self.save_error_report()
        
def setup_exception_handling():
    """Set up global exception handling"""
    def exception_handler(exctype, value, tb):
        error_tracker = ErrorTracker()
        error_tracker.track_error(exctype, str(value))
        
        # Log the full traceback
        traceback_str = ''.join(traceback.format_tb(tb))
        error_logger.error(f"Uncaught exception: {exctype.__name__}: {value}\n{traceback_str}")
        
        # Call the default exception handler
        sys.__excepthook__(exctype, value, tb)
    
    # Set the exception hook
    sys.excepthook = exception_handler

def catch_exceptions(func):
    """Decorator to catch and log exceptions in functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_tracker = ErrorTracker()
            error_tracker.track_error(type(e), str(e), func.__name__)
            error_logger.exception(f"Error in {func.__name__}: {e}")
            raise  # Re-raise the exception
    return wrapper

def ui_exception_handler(func):
    """Decorator to catch exceptions in UI operations and show message box"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            error_tracker = ErrorTracker()
            error_tracker.track_error(type(e), str(e), func.__name__)
            error_logger.exception(f"Error in UI operation {func.__name__}: {e}")
            
            QMessageBox.critical(
                self, 
                "Error", 
                f"An error occurred: {str(e)}\n\nThe error has been logged."
            )
    return wrapper

def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if duration > 1.0:  # Only log slow functions (> 1 second)
            logger.info(f"Performance: {func.__name__} took {duration:.2f} seconds to execute")
        
        return result
    return wrapper