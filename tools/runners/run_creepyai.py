#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to run CreepyAI with PyQt5 WebEngine compatibility
"""

import os
import sys
import logging
import subprocess
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CreepyAI.Runner')

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import PyQt5
        from PyQt5 import QtWebEngineWidgets
        logger.info("PyQt5 and QtWebEngineWidgets are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependencies: {str(e)}")
        logger.info("Please install required dependencies: pip install PyQt5 PyQtWebEngine")
        return False

def compile_resources():
    """Compile QRC resources if needed"""
    qrc_file = os.path.join(PROJECT_ROOT, 'resources', 'creepy_resources.qrc')
    output_file = os.path.join(PROJECT_ROOT, 'resources', 'creepy_resources_rc.py')
    
    # If resources are already compiled and newer than QRC, skip
    if os.path.exists(output_file) and os.path.getmtime(output_file) > os.path.getmtime(qrc_file):
        logger.info("Resource file already up to date")
        return True
    
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))
        from compile_resources import compile_resources as compile_rc
        if compile_rc(qrc_file, output_file):
            logger.info("Resources compiled successfully")
            return True
        else:
            logger.error("Failed to compile resources")
            return False
    except Exception as e:
        logger.error(f"Error compiling resources: {str(e)}")
        
        # Try direct pyrcc5 command as fallback
        try:
            logger.info("Trying direct pyrcc5 command...")
            result = subprocess.run(['pyrcc5', '-o', output_file, qrc_file], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Resources compiled successfully with pyrcc5 command")
                return True
            else:
                logger.error(f"pyrcc5 failed: {result.stderr}")
                return False
        except Exception as e2:
            logger.error(f"Failed to compile resources with direct command: {str(e2)}")
            return False

def patch_webengine_compatibility():
    """Create a compatibility layer for WebEngine"""
    compat_file = os.path.join(PROJECT_ROOT, 'utilities', 'webengine_compat.py')
    
    # Only create if it doesn't exist
    if os.path.exists(compat_file):
        logger.info("WebEngine compatibility layer already exists")
        return
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(compat_file), exist_ok=True)
        
    # Write the compatibility code to the file - fixed the nested triple quotes issue
    content = '''# -*- coding: utf-8 -*-
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
import logging

logger = logging.getLogger(__name__)

class WebEngineBridge(QObject):
    """Bridge between Python and JavaScript"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}
        
    @pyqtSlot(str, str)
    def setData(self, key, value):
        logger.debug(f"JS bridge: setData({key}, {value})")
        self._data[key] = value
        
    @pyqtSlot(str, result=str)
    def getData(self, key):
        logger.debug(f"JS bridge: getData({key})")
        return self._data.get(key, '')
        
    def addToPage(self, page, name='bridge'):
        from PyQt5.QtWebChannel import QWebChannel
        channel = QWebChannel(page)
        channel.registerObject(name, self)
        page.setWebChannel(channel)
        
        # Inject the web channel
        page.loadFinished.connect(lambda ok: self._inject_webchannel(page) if ok else None)
        
    def _inject_webchannel(self, page):
        script = \'\'\'
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.bridge = channel.objects.bridge;
        });
        \'\'\'
        page.runJavaScript(script)

class WebEnginePageCompat(QWebEnginePage):
    """Compatibility wrapper for QWebEnginePage"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bridge = WebEngineBridge(self)
        self._bridge.addToPage(self)
        self._javascript_objects = {}
        
    def mainFrame(self):
        return self  # Emulate the old-style API
        
    def addToJavaScriptWindowObject(self, name, obj):
        """Legacy method for compatibility"""
        self._javascript_objects[name] = obj
        # We'll need to expose properties/methods of this object via the bridge
        for attr_name in dir(obj):
            if not attr_name.startswith('_'):
                attr = getattr(obj, attr_name)
                if callable(attr):
                    # Create a function to call this method
                    setattr(self._bridge, attr_name, lambda *args, method=attr: method(*args))
        
    def setUrl(self, url):
        if isinstance(url, str):
            url = QUrl(url)
        super().setUrl(url)
        
    def evaluateJavaScript(self, code):
        """Legacy method for compatibility"""
        self.runJavaScript(code)
'''
    
    with open(compat_file, 'w') as f:
        f.write(content)
        
    logger.info("Created WebEngine compatibility layer")
    
    # Also need to patch imports in main file
    main_file = os.path.join(PROJECT_ROOT, 'CreepyMain.py')
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
            
        if 'from utilities.webengine_compat import WebEnginePageCompat' not in content:
            # Add import and replace QWebEnginePage with compat class
            content = content.replace(
                'from PyQt5.QtWebEngineWidgets import QWebEnginePage',
                'from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView\nfrom utilities.webengine_compat import WebEnginePageCompat'
            )
            content = content.replace('QWebEnginePage()', 'WebEnginePageCompat()')
            
            with open(main_file, 'w') as f:
                f.write(content)
                
            logger.info("Patched CreepyMain.py for WebEngine compatibility")
    else:
        logger.warning("Could not find CreepyMain.py to patch")

def run_creepyai():
    """Run the CreepyAI application"""
    try:
        # Change to project root
        os.chdir(PROJECT_ROOT)
        
        # Import the main module
        import creepy.CreepyMain as CreepyMain
        
        # If it has a main function, call it
        if hasattr(CreepyMain, 'main'):
            return CreepyMain.main()
        else:
            # Otherwise just import it (it should have a __main__ block)
            return 0
    except Exception as e:
        logger.error(f"Failed to run CreepyAI: {str(e)}", exc_info=True)
        return 1

def main():
    parser = argparse.ArgumentParser(description='Run CreepyAI with PyQt5 compatibility')
    parser.add_argument('--skip-resource-compile', action='store_true',
                        help='Skip resource compilation')
    parser.add_argument('--skip-dependency-check', action='store_true',
                        help='Skip dependency checks')
    args = parser.parse_args()
    
    # Check dependencies
    if not args.skip_dependency_check:
        if not check_dependencies():
            return 1
    
    # Compile resources
    if not args.skip_resource_compile:
        if not compile_resources():
            logger.warning("Resource compilation failed, will attempt to continue anyway")
    
    # Create WebEngine compatibility patch
    patch_webengine_compatibility()
    
    # Run the application
    return run_creepyai()

if __name__ == "__main__":
    sys.exit(main())
