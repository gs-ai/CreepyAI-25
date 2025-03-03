#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class AboutDialog(QDialog):
    """About dialog for the CreepyAI application."""
    
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        
        self.setWindowTitle("About CreepyAI")
        self.setFixedSize(400, 400)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(":/icons/logo")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # App name
        app_name = QLabel("CreepyAI")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        app_name.setFont(font)
        app_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description = QLabel(
            "<p>CreepyAI is a geolocation intelligence tool that collects and analyzes "
            "social media and online data to track and visualize user locations "
            "without relying on APIs.</p>"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Credits
        credits = QLabel(
            "<p><b>Created by:</b> CreepyAI Team</p>"
            "<p><b>License:</b> See LICENSE file</p>"
        )
        credits.setWordWrap(True)
        credits.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits)
        
        # Disclaimer
        disclaimer = QLabel(
            "<p><small>This software is provided for educational and research purposes only. "
            "Users are responsible for using this tool in an ethical and legal manner.</small></p>"
        )
        disclaimer.setWordWrap(True)
        disclaimer.setAlignment(Qt.AlignCenter)
        layout.addWidget(disclaimer)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)