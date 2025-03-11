"""
Logging configuration for CreepyAI.
"""
import os
import sys
import logging
import logging.config
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union

from .path_utils import get_user_log_dir, normalize_path

def setup_logger(name: str = 'creepyai', log_dir: Optional[str] = None, 
                level: Union[int, str] = logging.INFO) -> logging.Logger:
    """Set up and configure a logger.
    
    Args:
        name: Logger name
        log_dir: Directory for log files (uses default if None)
        level: Logging level (can be int constant or string level name)
        
    Returns:
        Configured logger instance
    """
    # Get numeric logging level from either int or string
    numeric_level = level
    if isinstance(level, str):
        numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers to avoid duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Set up file handler if log_dir is provided
    if log_dir:
        # Ensure log directory exists
        log_dir = normalize_path(log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        
        # Create file handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10 MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
        
        logger.info(f"Log file: {log_file}")
    
    # Log initialization
    logger.info(f"Logger {name} initialized with level {logging.getLevelName(numeric_level)}")
    
    return logger

def load_logging_config(config_file: str) -> bool:
    """Configure logging from JSON config file.
    
    Args:
        config_file: Path to logging config file
        
    Returns:
        True if configuration was loaded successfully
    """
    if not os.path.exists(config_file):
        logging.warning(f"Logging config file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Set up any directories in the config file
        for handler in config.get('handlers', {}).values():
            if 'filename' in handler:
                log_dir = os.path.dirname(handler['filename'])
                os.makedirs(log_dir, exist_ok=True)
        
        logging.config.dictConfig(config)
        return True
    except Exception as e:
        logging.error(f"Error loading logging config: {e}")
        return False
