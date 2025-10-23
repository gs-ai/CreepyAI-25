"""
PyQt utilities for CreepyAI.
Provides utilities for managing PyQt components.
"""
import os
import sys
import logging
import platform
import subprocess
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

logger = logging.getLogger('creepyai.utilities.pyqt')

# Global module availability flags
_QT_MODULES = {
    'core': False,
    'gui': False, 
    'widgets': False,
    'webengine': False
}

def initialize_qt():
    """Initialize Qt environment."""
    logger.info("Initializing PyQt...")
    
    try:
        # Import Qt modules
        from PyQt5 import QtCore
        logger.info("QtCore imported successfully")
        
        from PyQt5 import QtGui
        logger.info("QtGui imported successfully")
        
        from PyQt5 import QtWidgets
        logger.info("QtWidgets imported successfully")
        
        # Special handling for macOS
        if platform.system() == 'Darwin':
            # Set library paths for conda environments
            if 'CONDA_PREFIX' in os.environ:
                conda_prefix = os.environ['CONDA_PREFIX']
                
                # Ensure plugin paths are set correctly
                if not os.environ.get('QT_PLUGIN_PATH'):
                    plugin_path = os.path.join(conda_prefix, 'plugins')
                    if os.path.exists(plugin_path):
                        os.environ['QT_PLUGIN_PATH'] = plugin_path
                
                if not os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH'):
                    platform_path = os.path.join(conda_prefix, 'plugins', 'platforms')
                    if not os.path.exists(platform_path):
                        platform_path = os.path.join(conda_prefix, 'share', 'qt', 'plugins', 'platforms')
                    
                    if os.path.exists(platform_path):
                        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platform_path
                
                logger.info("Set conda library paths for macOS")

            # Fallback: if using PyQt5 wheels (pip) the plugins live under site-packages/PyQt5/Qt5/plugins
            try:
                import PyQt5  # type: ignore
                pyqt_dir = os.path.dirname(PyQt5.__file__)
                pyqt_plugins = os.path.join(pyqt_dir, 'Qt5', 'plugins')
                pyqt_platforms = os.path.join(pyqt_plugins, 'platforms')

                if not os.environ.get('QT_PLUGIN_PATH') and os.path.isdir(pyqt_plugins):
                    os.environ['QT_PLUGIN_PATH'] = pyqt_plugins
                    logger.info(f"Set QT_PLUGIN_PATH to PyQt plugins: {pyqt_plugins}")

                if not os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH') and os.path.isdir(pyqt_platforms):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = pyqt_platforms
                    logger.info(f"Set QT_QPA_PLATFORM_PLUGIN_PATH to PyQt platforms: {pyqt_platforms}")
            except Exception as _e:
                # Best-effort; continue if PyQt5 isn't importable yet
                pass
        
        # Import WebEngine if needed
        try:
            from PyQt5 import QtWebEngineWidgets
            logger.info("QtWebEngineWidgets imported successfully")
        except ImportError as e:
            logger.warning(f"QtWebEngineWidgets not available: {e}")
            logger.warning("Some features requiring web view will be disabled")
            
        logger.info("Qt initialized successfully")
        return True
    except ImportError as e:
        logger.error(f"Failed to initialize Qt: {e}")
        return False

def get_qt_version() -> Tuple[int, int, int]:
    """Get the Qt version.
    
    Returns:
        Tuple of (major, minor, patch) version numbers
    """
    try:
        from PyQt5.QtCore import QT_VERSION_STR
        version_str = QT_VERSION_STR
        parts = version_str.split('.')
        if len(parts) >= 3:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        return (0, 0, 0)
    except ImportError:
        return (0, 0, 0)

def get_pyqt_version() -> Tuple[int, int, int]:
    """Get the PyQt version.
    
    Returns:
        Tuple of (major, minor, patch) version numbers
    """
    try:
        from PyQt5.QtCore import PYQT_VERSION_STR
        version_str = PYQT_VERSION_STR
        parts = version_str.split('.')
        if len(parts) >= 3:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        return (0, 0, 0)
    except ImportError:
        return (0, 0, 0)

def is_webengine_available() -> bool:
    """Check if QtWebEngine is available.
    
    Returns:
        True if QtWebEngine is available, False otherwise
    """
    try:
        from PyQt5 import QtWebEngineWidgets
        return True
    except ImportError:
        return False

def init_pyqt():
    """
    Initialize PyQt and check available modules.
    
    Returns:
        Dict with status of each module
    """
    global _QT_MODULES
    
    logger.info("Initializing PyQt...")
    
    # Try to import core modules
    try:
        from PyQt5 import QtCore
        _QT_MODULES['core'] = True
        logger.info("QtCore imported successfully")
        
        from PyQt5 import QtGui
        _QT_MODULES['gui'] = True
        logger.info("QtGui imported successfully")
        
        from PyQt5 import QtWidgets
        _QT_MODULES['widgets'] = True
        logger.info("QtWidgets imported successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import core PyQt modules: {e}")
        return _QT_MODULES
    
    # Try to import WebEngine
    try:
        # Set platform-specific environment variables
        if platform.system() == 'Darwin':  # macOS
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"
            os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "0"
            
            # Check if we're in a conda environment
            if 'CONDA_PREFIX' in os.environ:
                conda_prefix = os.environ['CONDA_PREFIX']
                os.environ["DYLD_FRAMEWORK_PATH"] = f"{conda_prefix}/lib:{os.environ.get('DYLD_FRAMEWORK_PATH', '')}"
                os.environ["DYLD_LIBRARY_PATH"] = f"{conda_prefix}/lib:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
                logger.info(f"Set conda library paths for macOS")
        
        # Try to import WebEngine
        from PyQt5 import QtWebEngineWidgets
        _QT_MODULES['webengine'] = True
        logger.info("QtWebEngineWidgets imported successfully")
        
    except ImportError as e:
        logger.warning(f"Failed to import QtWebEngineWidgets: {e}")
        logger.warning("WebEngine not available - some features will be disabled")
    
    return _QT_MODULES

def get_qt_status() -> Dict[str, bool]:
    """Get status of Qt modules."""
    global _QT_MODULES
    return dict(_QT_MODULES)

def get_appropriate_gui_class():
    """
    Get appropriate GUI class based on available Qt modules.
    
    Returns:
        Class reference or import path to GUI class
    """
    if is_webengine_available():
        # Full featured GUI with WebEngine
        return 'src.gui.ui.main.creepyai_gui.CreepyAIGUI'
    else:
        # Fallback GUI without WebEngine
        return 'src.gui.ui.fallback.FallbackMainWindow'

def run_fix_script(show_output: bool = False) -> Tuple[bool, str]:
    """
    Run the PyQt fix script.
    
    Args:
        show_output: Whether to show script output
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Get script path
        project_root = Path(__file__).parent.parent.parent
        fix_script = project_root / "scripts" / "fix_pyqt.sh"
        
        if not fix_script.exists():
            return False, f"Fix script not found: {fix_script}"
        
        # Run the script
        result = subprocess.run(
            ["bash", str(fix_script)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if show_output:
                return True, f"Fix script executed successfully:\n{result.stdout}"
            return True, "Fix script executed successfully"
        else:
            return False, f"Fix script failed with code {result.returncode}:\n{result.stderr}"
            
    except Exception as e:
        return False, f"Error running fix script: {e}"

def get_qt_diagnostics() -> Dict[str, Any]:
    """
    Get detailed diagnostics about Qt installation.
    
    Returns:
        Dictionary with diagnostic information
    """
    diagnostics = {
        'qt_modules': get_qt_status(),
        'python_version': sys.version,
        'platform': platform.platform()
    }
    
    # Check PyQt installation paths
    try:
        import PyQt5
        diagnostics['pyqt_path'] = PyQt5.__path__[0]
    except (ImportError, AttributeError):
        diagnostics['pyqt_path'] = "Not found"
    
    # Check for conda environment
    diagnostics['conda_env'] = os.environ.get('CONDA_PREFIX', "Not in conda environment")
    
    # Check library paths
    diagnostics['library_paths'] = {
        'LD_LIBRARY_PATH': os.environ.get('LD_LIBRARY_PATH', ''),
        'DYLD_LIBRARY_PATH': os.environ.get('DYLD_LIBRARY_PATH', ''),
        'DYLD_FRAMEWORK_PATH': os.environ.get('DYLD_FRAMEWORK_PATH', ''),
    }
    
    return diagnostics
