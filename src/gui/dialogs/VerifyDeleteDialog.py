# Note: This file was moved from components/VerifyDeleteDialog.py to ui/

#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

class VerifyDeleteDialog(QDialog):
    """Dialog to confirm deletion of a project."""
    
    def __init__(self, parent=None):
        super(VerifyDeleteDialog, self).__init__(parent)
        self.setWindowTitle("Confirm Deletion")
        self.setupUI()
        
    def setupUI(self):
        # Create layout
        layout = QVBoxLayout(self)
        
        # Warning icon and message
        message_layout = QVBoxLayout()
        
        # Warning icon
        self.warning_icon = QLabel(self)
        self.warning_icon.setPixmap(QPixmap(':/creepy/exclamation').scaled(48, 48, Qt.KeepAspectRatio))
        self.warning_icon.setAlignment(Qt.AlignCenter)
        message_layout.addWidget(self.warning_icon)
        
        # Warning message
        self.label = QLabel(self)
        self.label.setText("Are you sure you want to delete the project '@project@'?\n\nThis action cannot be undone.")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        message_layout.addWidget(self.label)
        
        layout.addLayout(message_layout)
        
        # Additional warning checkbox
        self.confirm_check = QCheckBox("I understand this will permanently delete all project data", self)
        layout.addWidget(self.confirm_check)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.verify_and_accept)
        self.button_box.rejected.connect(self.reject)
        
        # Make the OK button red to indicate danger
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Delete")
        
        layout.addWidget(self.button_box)
        
    def verify_and_accept(self):
        """Verify the checkbox is checked before accepting"""
        if self.confirm_check.isChecked():
            self.accept()
