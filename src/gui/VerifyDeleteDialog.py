#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox
from resources.icons import Icons
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

class VerifyDeleteDialog(QDialog):
    """Dialog to verify deletion of items."""
    
    def __init__(self, item_name, parent=None):
        super(VerifyDeleteDialog, self).__init__(parent)
        
        self.setWindowTitle("Confirm Deletion")
        self.setFixedWidth(400)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Warning icon and message
        icon_layout = QHBoxLayout()
        icon_label = QLabel()
        warning_icon = Icons.get_pixmap("warning")
        if not warning_icon.isNull():
            icon_label.setPixmap(warning_icon.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_layout.addWidget(icon_label)
        
        message_label = QLabel(f"Are you sure you want to delete '{item_name}'?\nThis action cannot be undone.")
        message_label.setWordWrap(True)
        icon_layout.addWidget(message_label)
        
        layout.addLayout(icon_layout)
        
        # Don't ask again checkbox
        self.dont_ask_check = QCheckBox("Don't ask me again")
        layout.addWidget(self.dont_ask_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_button.clicked.connect(self.accept)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def should_remember(self):
        """Check if the user wants to remember their choice."""
        return self.dont_ask_check.isChecked()
