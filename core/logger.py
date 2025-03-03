import logging
import os
import sys
from datetime import datetime
import traceback

def setup_logger(log_level=logging.INFO, log_file=None):
    """
    Configure logging for the application.
    
    Args:
        log_level: The logging level to use
        log_file: Path to log file, if None uses default location
    """
    if not log_file:
        log_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "logs")
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"creepyai_{date_str}.log")
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log uncaught exceptions
    def exception_handler(exc_type, exc_value, exc_traceback):
        logger.critical("Uncaught exception", 
                       exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_handler
    
    logger.info(f"Logging initialized at level {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_file}")
    
    return logger
