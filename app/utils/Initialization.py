#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from models.Database import Database
from utilities.ResourceLoader import ResourceLoader
from models.PluginManager import PluginManager

logger = logging.getLogger(__name__)

class AppInitializer:
    """
    Handles application initialization steps in the correct order:
    1. Pre-initialization (logging, directories, etc.)
    2. QApplication creation
    3. Post-initialization (database, plugins, etc.)
    """
    
    def __init__(self):
        self.app = None
        self.splash = None
        self.database = None
        self.resource_loader = None
        self.plugin_manager = None
    
    def pre_init(self):
        """
        Perform tasks that need to happen before QApplication creation
        """
        # Set up logging
        self._setup_logging()
        
        # Create necessary directories
        self._create_directories()
        
        # Initialize ResourceLoader early
        self.resource_loader = ResourceLoader.instance()
        
        # Add the project root directory to the path
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_dir not in sys.path:
            sys.path.insert(0, project_dir)
        
        # Set up Qt environment variables if needed
        if "QT_PLUGIN_PATH" not in os.environ:
            conda_prefix = os.environ.get('CONDA_PREFIX')
            if conda_prefix:
                possible_plugin_paths = [
                    os.path.join(conda_prefix, 'plugins'),
                    os.path.join(conda_prefix, 'lib/qt/plugins'),
                ]
                
                for path in possible_plugin_paths:
                    if os.path.exists(path):
                        os.environ['QT_PLUGIN_PATH'] = path
                        break
        
        logger.info("Pre-initialization complete")
    
    def init_app(self):
        """
        Create QApplication and splash screen
        
        Returns:
            QApplication instance
        """
        # Enable high DPI scaling
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("CreepyAI")
        self.app.setOrganizationName("CreepyAI")
        
        # Show splash screen if available
        splash_pixmap = self.resource_loader.get_pixmap('splash', 'app_icon')
        if not splash_pixmap.isNull():
            self.splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
            self.splash.show()
            self.splash.showMessage("Starting CreepyAI...", Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
            self.app.processEvents()
        
        logger.info("Application initialized")
        return self.app
    
    def post_init(self):
        """
        Perform tasks after QApplication creation
        """
        # Initialize database
        self._init_database()
        
        # Initialize plugin system
        self._init_plugins()
        
        # Load stylesheet if available
        self._load_stylesheet()
        
        # Close splash screen after short delay
        if self.splash:
            QTimer.singleShot(1500, self.splash.close)
        
        # Set application style
        self.app.setStyle("Fusion")
        
        logger.info("Post-initialization complete")
    
    def _setup_logging(self):
        """Set up logging system"""
        # Create logs directory
        log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Add file handler
        log_path = os.path.join(log_dir, 'creepyai.log')
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(file_handler)
        
        logger.info("Logging system initialized")
    
    def _create_directories(self):
        """Create necessary directories"""
        # Home directory for configuration and data
        app_dir = os.path.join(os.path.expanduser("~"), '.creepyai')
        os.makedirs(app_dir, exist_ok=True)
        
        # Logs directory
        log_dir = os.path.join(app_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Cache directory
        cache_dir = os.path.join(app_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Projects directory
        projects_dir = os.path.join(os.getcwd(), 'projects')
        os.makedirs(projects_dir, exist_ok=True)
        
        # Plugins directory
        plugins_dir = os.path.join(os.getcwd(), 'plugins')
        os.makedirs(plugins_dir, exist_ok=True)
        
        logger.debug("Directory structure created")
    
    def _init_database(self):
        """Initialize the database"""
        try:
            db_path = os.path.join(os.path.expanduser("~"), '.creepyai', 'creepyai.db')
            self.database = Database(db_path)
            logger.info(f"Database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
    
    def _init_plugins(self):
        """Initialize plugin system"""
        try:
            self.plugin_manager = PluginManager.get_instance()
            self.plugin_manager.set_plugin_paths([
                os.path.join(os.getcwd(), 'plugins')
            ])
            logger.info("Plugin system initialized")
        except Exception as e:
            logger.error(f"Plugin initialization error: {str(e)}")
    
    def _load_stylesheet(self):
        """Load application stylesheet"""
        try:
            style_path = self.resource_loader.get_resource_path('styles', 'main')
            if style_path:
                with open(style_path, 'r') as f:
                    self.app.setStyleSheet(f.read())
                logger.info("Stylesheet applied")
        except Exception as e:
            logger.warning(f"Could not load stylesheet: {str(e)}")
