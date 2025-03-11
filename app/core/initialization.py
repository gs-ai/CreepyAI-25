"""
Application Initialization Module
Handles application startup procedures and initialization of components
"""

import os
import sys
import logging
import shutil
import platform
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import QSettings

from app.core.path_utils import (
    get_app_root, get_user_data_dir, get_user_config_dir,
    get_user_log_dir, get_user_cache_dir, ensure_app_dirs
)

logger = logging.getLogger(__name__)

def initialize_app() -> Dict[str, Any]:
    """
    Initialize application components
    
    Returns:
        Dictionary with initialization status and info
    """
    results = {
        'success': True,
        'components': {},
        'errors': [],
    }
    
    # Initialize data directories
    data_dirs = _initialize_directories()
    results['components']['directories'] = data_dirs
    
    # Initialize themes
    theme_status = _initialize_theme_system()
    results['components']['themes'] = theme_status
    
    # Initialize plugins
    plugin_status = _initialize_plugin_system()
    results['components']['plugins'] = plugin_status
    
    # Initialize logging
    log_status = _initialize_logging()
    results['components']['logging'] = log_status
    
    # Check for first run
    results['first_run'] = _is_first_run()
    
    # Collect any errors
    for component, status in results['components'].items():
        if 'error' in status and status['error']:
            results['errors'].append(f"{component}: {status['error']}")
            
    # Overall success status
    if results['errors']:
        results['success'] = False
    
    return results

def _initialize_directories() -> Dict[str, Any]:
    """
    Initialize application directories
    
    Returns:
        Dictionary with directory paths and creation status
    """
    result = {
        'success': True,
        'error': None,
        'paths': {}
    }
    
    try:
        # Get base application data directory
        settings = QSettings("CreepyAI", "Application")
        data_dir = settings.value("dataDirectory", "")
        
        # If no directory is configured, use default
        if not data_dir:
            data_dir = str(get_user_data_dir())
            settings.setValue("dataDirectory", data_dir)
        
        # Ensure directories exist
        ensure_app_dirs()
        
        # Store paths in result
        result['paths']['app_root'] = str(get_app_root())
        result['paths']['data_dir'] = data_dir
        result['paths']['config_dir'] = str(get_user_config_dir())
        result['paths']['log_dir'] = str(get_user_log_dir())
        result['paths']['cache_dir'] = str(get_user_cache_dir())
        
        # Create subdirectories within data directory
        subdirs = [
            'logs',
            'plugins',
            'exports',
            'reports',
            'cache',
            'temp'
        ]
        
        for subdir in subdirs:
            path = os.path.join(data_dir, subdir)
            os.makedirs(path, exist_ok=True)
            result['paths'][subdir] = path
        
        # Create symbolic link to resources if needed
        resource_path = os.path.join(get_app_root(), 'app', 'resources')
        if os.path.exists(resource_path):
            result['paths']['resources'] = resource_path
        
        logger.info(f"Data directory: {data_dir}")
        
    except Exception as e:
        result['success'] = False
        result['error'] = f"Failed to initialize directories: {str(e)}"
        logger.error(f"Directory initialization error: {e}", exc_info=True)
    
    return result

def _initialize_theme_system() -> Dict[str, Any]:
    """
    Initialize the theme system
    
    Returns:
        Dictionary with theme initialization status
    """
    result = {
        'success': True,
        'error': None
    }
    
    try:
        # Check for theme CSS files
        app_root = get_app_root()
        dark_theme_path = os.path.join(app_root, 'app', 'core', 'include', 'style_dark.qss')
        
        if not os.path.exists(dark_theme_path):
            logger.warning("Dark theme stylesheet not found")
            result['warning'] = "Dark theme stylesheet not found"
        
        # Get theme preference
        settings = QSettings("CreepyAI", "Application")
        theme_pref = settings.value("theme", "system")
        result['current_theme'] = theme_pref
        
    except Exception as e:
        result['success'] = False
        result['error'] = f"Failed to initialize theme system: {str(e)}"
        logger.error(f"Theme initialization error: {e}", exc_info=True)
    
    return result

def _initialize_plugin_system() -> Dict[str, Any]:
    """
    Initialize the plugin system
    
    Returns:
        Dictionary with plugin initialization status
    """
    result = {
        'success': True,
        'error': None,
        'plugins': []
    }
    
    try:
        # Check plugin paths
        user_data_dir = get_user_data_dir()
        plugin_dir = user_data_dir / 'plugins'
        plugin_dir.mkdir(exist_ok=True)
        
        # Look for plugin configuration file
        app_root = get_app_root()
        plugin_config_path = os.path.join(app_root, 'configs', 'plugins', 'plugins.yaml')
        
        if not os.path.exists(plugin_config_path):
            logger.warning("Plugin configuration file not found")
            result['warning'] = "Plugin configuration file not found"
        else:
            result['config_path'] = plugin_config_path
        
        # Get list of built-in plugins
        try:
            from app.plugin_registry import register_plugins
            available_plugins = register_plugins()
            result['plugins'] = [p.__name__ for p in available_plugins]
            logger.info(f"Found {len(available_plugins)} built-in plugins")
        except ImportError as e:
            result['warning'] = f"Could not load plugin registry: {str(e)}"
            logger.warning(f"Could not load plugin registry: {e}")
        
    except Exception as e:
        result['success'] = False
        result['error'] = f"Failed to initialize plugin system: {str(e)}"
        logger.error(f"Plugin initialization error: {e}", exc_info=True)
    
    return result

def _initialize_logging() -> Dict[str, Any]:
    """
    Initialize the logging system
    
    Returns:
        Dictionary with logging initialization status
    """
    result = {
        'success': True,
        'error': None,
    }
    
    try:
        # Set up logging using the logger_setup module
        from app.core.include.logger_setup import setup_logging
        
        log_dir = get_user_log_dir()
        log_file = os.path.join(log_dir, f"creepyai_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Get log level from settings
        settings = QSettings("CreepyAI", "Application")
        log_level_name = settings.value("log_level", "INFO")
        
        # Map string log level to numeric value
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        log_level = log_levels.get(log_level_name, logging.INFO)
        
        # Initialize logger
        setup_logging(log_file, log_level)
        result['log_file'] = log_file
        result['log_level'] = log_level_name
        
        logger.info(f"Logging initialized with level {log_level_name}")
        
    except Exception as e:
        result['success'] = False
        result['error'] = f"Failed to initialize logging: {str(e)}"
        print(f"Logging initialization error: {e}")
    
    return result

def _is_first_run() -> bool:
    """
    Check if this is the first run of the application
    
    Returns:
        True if this is the first run, False otherwise
    """
    settings = QSettings("CreepyAI", "Application")
    first_run = settings.value("firstRun", True, bool)
    return first_run

def initialize_language() -> Dict[str, Any]:
    """
    Initialize language settings
    
    Returns:
        Dictionary with language initialization status
    """
    result = {
        'success': True,
        'error': None,
        'language': 'en'
    }
    
    try:
        # Get language preference
        settings = QSettings("CreepyAI", "Application")
        language = settings.value("language", "en")
        result['language'] = language
        
        # Check for translation files
        app_root = get_app_root()
        translation_path = os.path.join(app_root, 'app', 'resources', 'translations', f"{language}.qm")
        
        if language != 'en' and not os.path.exists(translation_path):
            logger.warning(f"Translation file for {language} not found")
            result['warning'] = f"Translation file for {language} not found"
        
    except Exception as e:
        result['success'] = False
        result['error'] = f"Failed to initialize language: {str(e)}"
        logger.error(f"Language initialization error: {e}", exc_info=True)
    
    return result

def initialize_database() -> Dict[str, Any]:
    """
    Initialize database connection
    
    Returns:
        Dictionary with database initialization status
    """
    result = {
        'success': True,
        'error': None
    }
    
    try:
        # Get database path
        settings = QSettings("CreepyAI", "Application")
        data_dir = settings.value("dataDirectory", "")
        if not data_dir:
            data_dir = str(get_user_data_dir())
        
        db_path = os.path.join(data_dir, 'creepyai.db')
        result['db_path'] = db_path
        
        # Initialize database connection
        # This would typically create tables if they don't exist
        # For now, just check if the file exists
        if not os.path.exists(db_path):
            # Create empty file
            with open(db_path, 'w') as f:
                pass
            logger.info(f"Created new database file: {db_path}")
        
    except Exception as e:
        result['success'] = False
        result['error'] = f"Failed to initialize database: {str(e)}"
        logger.error(f"Database initialization error: {e}", exc_info=True)
    
    return result
