import os
import sys
import logging
import glob
from PyQt5.QtCore import QCoreApplication

logger = logging.getLogger('creepyai.utilities.webengine')

def detect_qt_conflicts():
    """Detect potential Qt library conflicts."""
    if 'CONDA_PREFIX' in os.environ:
        conda_prefix = os.environ['CONDA_PREFIX']
        
        # Check for duplicate Qt libraries
        lib_qt_core = os.path.join(conda_prefix, 'lib', 'libQt5Core.*.dylib')
        pyqt_qt_core = os.path.join(conda_prefix, 'lib', 'python3.11', 'site-packages', 'PyQt5', 'Qt5', 'lib', 'QtCore.framework')
        
        has_lib_qt = len(glob.glob(lib_qt_core)) > 0
        has_pyqt_qt = os.path.exists(pyqt_qt_core)
        
        if has_lib_qt and has_pyqt_qt:
            logger.warning("Detected potential Qt library conflict!")
            logger.warning(f"Found Qt libraries in conda lib dir: {has_lib_qt}")
            logger.warning(f"Found Qt libraries in PyQt5 dir: {has_pyqt_qt}")
            return True
    
    return False

def resolve_qt_conflicts():
    """Attempt to resolve Qt conflicts automatically."""
    if not detect_qt_conflicts():
        return True
        
    logger.info("Attempting to resolve Qt conflicts automatically...")
    
    # Create qt.conf if needed
    if 'CONDA_PREFIX' in os.environ:
        conda_prefix = os.environ['CONDA_PREFIX']
        pyqt_dir = os.path.join(conda_prefix, 'lib', 'python3.11', 'site-packages', 'PyQt5')
        
        # Create qt.conf to direct Qt to use conda libraries
        if os.path.exists(pyqt_dir):
            qt_conf_path = os.path.join(pyqt_dir, 'qt.conf')
            with open(qt_conf_path, 'w') as f:
                f.write("[Paths]\n")
                f.write(f"Prefix = {conda_prefix}\n")
                f.write(f"Libraries = {os.path.join(conda_prefix, 'lib')}\n")
                f.write(f"Plugins = {os.path.join(conda_prefix, 'plugins')}\n")
                logger.info(f"Created qt.conf at: {qt_conf_path}")
    
    return True

def init_qt_webengine():
    """Initialize QtWebEngine with proper path settings."""
    try:
        # Check for and resolve Qt conflicts
        resolve_qt_conflicts()
        
        import PyQt5
        pyqt_dir = os.path.dirname(PyQt5.__file__)
        logger.info(f"PyQt5 directory: {pyqt_dir}")
        
        # Set paths for QtWebEngine on macOS
        if sys.platform == 'darwin':
            # Fix Qt library path conflicts on macOS
            # We need to ensure only one set of Qt libraries is loaded
            conda_prefix = os.environ.get('CONDA_PREFIX')
            
            if conda_prefix:
                # Configure paths properly for conda environment
                platforms_path = find_directory(conda_prefix, 'platforms', 
                                            subdirs=['plugins', 'share/qt/plugins'])
                if platforms_path:
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_path
                    logger.info(f"Set QT_QPA_PLATFORM_PLUGIN_PATH to: {platforms_path}")
                
                # Set library path to conda lib directory to ensure correct Qt libraries are used
                lib_path = os.path.join(conda_prefix, 'lib')
                if os.path.exists(lib_path):
                    QCoreApplication.setLibraryPaths([lib_path])
                    logger.info(f"Set Qt library path to: {lib_path}")
                
                # Disable sandbox for better compatibility
                os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
                os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --no-sandbox --disable-dev-shm-usage'
                
                # Find QtWebEngineProcess and set proper permissions
                webengine_process_path = find_qtwebengine_process(conda_prefix, pyqt_dir)
                if webengine_process_path:
                    os.environ['QTWEBENGINEPROCESS_PATH'] = webengine_process_path
                    logger.info(f"Set QTWEBENGINEPROCESS_PATH to: {webengine_process_path}")
                    # Ensure it's executable
                    if not os.access(webengine_process_path, os.X_OK):
                        os.chmod(webengine_process_path, 0o755)
                        logger.info(f"Set executable permission on QtWebEngineProcess")
            else:
                # For non-conda environments, use the PyQt bundled libraries
                QCoreApplication.setLibraryPaths([os.path.join(pyqt_dir, 'Qt5', 'plugins')])
                logger.info(f"Set library paths to: {os.path.join(pyqt_dir, 'Qt5', 'plugins')}")
            
            # Import WebEngine to ensure it's loaded
            try:
                from PyQt5 import QtWebEngineWidgets
                logger.info("Successfully imported QtWebEngineWidgets")
            except Exception as e:
                logger.error(f"Failed to import QtWebEngineWidgets: {e}")
            
            return True
        return False
    except Exception as e:
        logger.error(f"Error initializing QtWebEngine: {e}")
        return False

def find_directory(base_dir, target_dir, subdirs=None):
    """Find directory in possible subdirectories."""
    if not subdirs:
        subdirs = ['']
    
    for subdir in subdirs:
        path = os.path.join(base_dir, subdir, target_dir)
        if os.path.exists(path) and os.path.isdir(path):
            return path
    return None

def find_qtwebengine_process(conda_prefix, pyqt_dir):
    """Find QtWebEngineProcess executable in various possible locations."""
    # Try standard locations first
    locations = [
        os.path.join(pyqt_dir, 'Qt5', 'libexec', 'QtWebEngineProcess'),
        os.path.join(conda_prefix, 'libexec', 'QtWebEngineProcess'),
        os.path.join(conda_prefix, 'bin', 'QtWebEngineProcess')
    ]
    
    for location in locations:
        if os.path.exists(location):
            return location
    
    # If not found, search recursively (but with limitations to avoid excessive searching)
    search_paths = [
        os.path.join(conda_prefix, 'libexec'),
        os.path.join(conda_prefix, 'lib'),
        os.path.join(conda_prefix, 'share')
    ]
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            matches = glob.glob(os.path.join(base_path, '**/QtWebEngineProcess'), recursive=True)
            if matches:
                return matches[0]
    
    logger.warning("QtWebEngineProcess not found in any standard locations")
    return None

# Auto-initialize when imported in macOS
if sys.platform == 'darwin':
    init_qt_webengine()
