#!/usr/bin/env python3
"""
Main entry point for CreepyAI application.
"""
import os
import sys
import logging
import argparse
import traceback
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('creepyai')
logger.setLevel(logging.INFO)
logger.info("Logger creepyai initialized with level INFO")

# Get project root (repository root, not the ``app`` package directory)
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)

# Add project root to Python path so ``import app`` works reliably
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import utilities
try:
    from app.core.path_utils import get_app_root, get_user_log_dir, ensure_app_dirs
    from app.utilities.pyqt_manager import initialize_qt
    
    # Ensure necessary directories exist
    ensure_app_dirs()
except ImportError as e:
    logger.critical(f"Failed to import core modules: {e}")
    logger.debug(traceback.format_exc())
    sys.exit(1)

def setup_logging(log_level=logging.INFO):
    """Set up logging configuration."""
    logger.info("Starting CreepyAI")
    
    # Create logs directory in user space
    log_dir = get_user_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log file with timestamp
    from datetime import datetime
    log_filename = f"creepyai_{datetime.now().strftime('%Y%m%d')}.log"
    log_file = os.path.join(log_dir, log_filename)
    
    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Set log level
    logger.setLevel(log_level)
    
    logger.info(f"Log file: {log_file}")
    logger.info("Logger creepyai initialized with level INFO")

def initialize_application():
    """Initialize the CreepyAI application"""
    # Initialize plugin manager and register all plugins
    from app.plugin_registry import register_plugins
    from app.plugins.plugin_manager import PluginManager
    
    # Create plugin manager first
    plugin_manager = PluginManager()
    plugin_manager.initialize()
    
    # Register plugins with the manager
    all_plugins = register_plugins()
    plugin_manager.register_plugins(all_plugins)
    
    # Verify social media plugins are loaded
    social_media_plugins = [p for p in all_plugins if p.__name__ in [
        "FacebookPlugin", "InstagramPlugin", "LinkedInPlugin", "PinterestPlugin", 
        "SnapchatPlugin", "TikTokPlugin", "TwitterPlugin", "YelpPlugin"
    ]]
    
    logger.info(f"Loaded {len(social_media_plugins)} social media plugins")
    return plugin_manager

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CreepyAI - OSINT Location Intelligence")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--project", help="Open specified project")
    parser.add_argument("--fix-pyqt", action="store_true", help="Run PyQt fix script")
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    # Run PyQt fix if requested
    if args.fix_pyqt:
        try:
            from app.utilities.pyqt_manager import run_fix_script
            success, message = run_fix_script(True)
            if success:
                logger.info(f"PyQt fix script executed successfully")
            else:
                logger.error(f"PyQt fix failed: {message}")
            return 0
        except Exception as e:
            logger.error(f"Error running PyQt fix: {e}")
            return 1
    
    # Initialize application core
    try:
        from app.core.initialization import initialize_app
        initialize_app()
    except Exception as e:
        logger.critical(f"Failed to initialize application: {e}")
        logger.debug(traceback.format_exc())
        return 1
    
    # Load plugins
    logger.info("Loading plugins...")
    plugin_manager = None
    try:
        plugin_manager = initialize_application()
    except Exception as e:
        logger.error(f"Failed to load plugins: {e}")
        logger.debug(traceback.format_exc())
    
    # Run in appropriate mode
    if args.cli:
        logger.info("Starting CLI mode")
        try:
            from app.plugins.plugin_cli import PluginCLI

            cli = PluginCLI()
            if plugin_manager is not None:
                cli.manager = plugin_manager  # Reuse initialised manager
            return cli.run([])
        except Exception as exc:
            logger.error("CLI mode failed: %s", exc)
            logger.debug(traceback.format_exc())
            return 1
    else:
        # Initialize Qt first
        if not initialize_qt():
            logger.error("Failed to initialize Qt - cannot start GUI")
            return 1
            
        logger.info("Starting GUI mode")
        try:
            from app.utilities.pyqt_manager import get_appropriate_gui_class, is_webengine_available
            
            # Import PyQt
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication(sys.argv)
            app.setApplicationName("CreepyAI")
            # Apply global dark theme stylesheet
            try:
                from app.core.path_utils import get_app_root
                qss_path = get_app_root() / 'resources' / 'styles' / 'dark.qss'
                if qss_path.exists():
                    with open(qss_path, 'r', encoding='utf-8') as f:
                        app.setStyleSheet(f.read())
            except Exception as _e:
                logger.warning(f"Could not apply dark theme stylesheet: {_e}")
            
            # Dynamically load appropriate GUI class
            if is_webengine_available():
                from app.gui.ui.main.creepyai_gui import CreepyAIGUI
                window = CreepyAIGUI(plugin_manager=plugin_manager)
            else:
                from app.gui.ui.fallback import FallbackMainWindow
                window = FallbackMainWindow(plugin_manager=plugin_manager)
                
            window.show()
            return app.exec_()
            
        except Exception as e:
            logger.critical(f"Fatal error: {e}")
            logger.debug(traceback.format_exc())
            return 1

if __name__ == "__main__":
    sys.exit(main())
