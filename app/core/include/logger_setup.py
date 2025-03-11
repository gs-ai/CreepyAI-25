"""
Logger Setup for CreepyAI
Configures logging system for the application
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, List


def setup_logging(log_file: str, log_level: int = logging.INFO, 
                 console_level: Optional[int] = None) -> None:
    """
    Initialize the application's logging system
    
    Args:
        log_file: Path to the log file
        log_level: Logging level for the file handler
        console_level: Logging level for the console handler (if None, uses log_level)
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all logs at root level
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Set up console handler
    if console_level is None:
        console_level = log_level
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create app-specific logger
    app_logger = logging.getLogger('creepyai')
    app_logger.setLevel(log_level)
    
    # Log startup information
    app_logger.info("==== CreepyAI Logging Started ====")
    app_logger.info(f"Log file: {log_file}")
    app_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    app_logger.debug("Logger setup complete")


class LoggerFilter(logging.Filter):
    """
    Custom filter to exclude certain log messages
    
    Can be used to exclude noisy log messages from specific modules.
    """
    
    def __init__(self, patterns: Optional[List[str]] = None):
        super().__init__()
        self.patterns = patterns or []
    
    def filter(self, record):
        # If no patterns, include everything
        if not self.patterns:
            return True
        
        # Check if any pattern exists in the log message
        message = record.getMessage().lower()
        for pattern in self.patterns:
            if pattern.lower() in message:
                return False
                
        return True


def enable_debug_logging() -> None:
    """
    Enable debug logging for the application
    
    This can be called at runtime to switch to debug logging.
    """
    root_logger = logging.getLogger()
    
    for handler in root_logger.handlers:
        handler.setLevel(logging.DEBUG)
    
    app_logger = logging.getLogger('creepyai')
    app_logger.setLevel(logging.DEBUG)
    app_logger.debug("Debug logging enabled")


def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        module_name: Name of the module
    
    Returns:
        Logger configured for the specific module
    """
    return logging.getLogger(f"creepyai.{module_name}")


def configure_plugin_logger(plugin_name: str) -> logging.Logger:
    """
    Configure and return a logger specifically for plugins
    
    Args:
        plugin_name: Name of the plugin
    
    Returns:
        Logger configured for the specific plugin
    """
    logger = logging.getLogger(f"creepyai.plugins.{plugin_name}")
    return logger
