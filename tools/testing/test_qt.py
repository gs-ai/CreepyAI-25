#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple PyQt5 test script to verify the environment is working correctly.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CreepyAI Test Window")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Add test components
        header = QLabel("CreepyAI Environment Test")
        header.setAlignment(Qt.AlignCenter)
        font = header.font()
        font.setPointSize(16)
        header.setFont(font)
        layout.addWidget(header)
        
        # Version info
        import PyQt5
        version_label = QLabel(f"PyQt5 Version: {PyQt5.QtCore.PYQT_VERSION_STR}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Test buttons
        test_button = QPushButton("Test Button (Click Me)")
        test_button.clicked.connect(lambda: self.statusBar().showMessage("Button clicked successfully!"))
        layout.addWidget(test_button)
        
        # Icon test
        icon_button = QPushButton("Test Icon Loading")
        try:
            # Try to load an icon from resources
            icon = QIcon(':/creepy/folder')
            icon_button.setIcon(icon)
            icon_button.clicked.connect(lambda: self.statusBar().showMessage("Icon loaded successfully!"))
        except Exception as e:
            icon_button.setText(f"Icon loading failed: {str(e)}")
        layout.addWidget(icon_button)
        
        # Add some environment info
        env_info = f"""
        Python: {sys.version}
        Working Directory: {os.getcwd()}
        Display: {os.environ.get('DISPLAY', 'Not set')}
        """
        info_label = QLabel(env_info)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Set status bar
        self.statusBar().showMessage("Test window loaded successfully")

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Set application details
    app.setApplicationName("CreepyAI-Test")
    app.setOrganizationName("CreepyAI")
    
    # Create and show the main window
    window = TestWindow()
    window.show()
    
    # Run the application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
