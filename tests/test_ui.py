#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple UI test for CreepyAI.

This script creates a minimal PyQt5 window to test that the Qt environment
is properly configured. If this works, the main application should work as well.
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CreepyAI.UITest')

def test_pyqt():
    """Create and show a simple PyQt5 window to test the setup."""
    try:
        # Set up Qt environment
        from qt_setup import setup_qt_environment
        setup_qt_environment()
        
        # Import PyQt5 - Fix: Import the full module first
        import PyQt5
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
        from PyQt5.QtCore import Qt
        
        # Create the application
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create the main window
        window = QMainWindow()
        window.setWindowTitle("CreepyAI - PyQt5 Test")
        window.setGeometry(100, 100, 400, 300)
        
        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("PyQt5 is working correctly!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Add information about the Qt version
        version_label = QLabel(f"PyQt5 Version: {PyQt5.QtCore.PYQT_VERSION_STR}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        qt_label = QLabel(f"Qt Version: {PyQt5.QtCore.QT_VERSION_STR}")
        qt_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qt_label)
        
        # Add a button to close
        close_button = QPushButton("Close")
        close_button.clicked.connect(window.close)
        layout.addWidget(close_button)
        
        # Set the central widget
        window.setCentralWidget(central_widget)
        
        # Show the window
        window.show()
        
        logger.info("PyQt5 test window created successfully")
        return app.exec_()
        
    except ImportError as e:
        logger.error(f"Failed to import PyQt5: {e}")
        print(f"Error: Could not import PyQt5. {e}")
        return 1
    except Exception as e:
        logger.error(f"Error in PyQt5 test: {e}")
        print(f"Error: {e}")
        return 1

def test_webengine():
    """Test PyQtWebEngine functionality."""
    try:
        # Set up Qt environment
        from qt_setup import setup_qt_environment
        setup_qt_environment()
        
        # Import PyQt5 and WebEngine - Fix: Import the full module first
        import PyQt5
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
        from PyQt5.QtCore import QUrl
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        
        # Create the application
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create the main window
        window = QMainWindow()
        window.setWindowTitle("CreepyAI - WebEngine Test")
        window.setGeometry(100, 100, 800, 600)
        
        # Create a central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create a web view
        web_view = QWebEngineView()
        web_view.setUrl(QUrl("https://www.openstreetmap.org"))
        layout.addWidget(web_view)
        
        # Add a button to close
        close_button = QPushButton("Close")
        close_button.clicked.connect(window.close)
        layout.addWidget(close_button)
        
        # Set the central widget
        window.setCentralWidget(central_widget)
        
        # Show the window
        window.show()
        
        logger.info("WebEngine test window created successfully")
        return app.exec_()
        
    except ImportError as e:
        logger.error(f"Failed to import WebEngine: {e}")
        print(f"Error: Could not import PyQtWebEngine. {e}")
        return 1
    except Exception as e:
        logger.error(f"Error in WebEngine test: {e}")
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test CreepyAI UI')
    parser.add_argument('--webengine', action='store_true', help='Test PyQtWebEngine functionality')
    args = parser.parse_args()
    
    print("CreepyAI UI Test")
    print("=" * 50)
    
    if args.webengine:
        print("Testing PyQtWebEngine...")
        sys.exit(test_webengine())
    else:
        print("Testing basic PyQt5...")
        sys.exit(test_pyqt())
