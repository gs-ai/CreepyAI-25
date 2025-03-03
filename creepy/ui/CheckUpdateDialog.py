#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import json
import logging
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from packaging import version

logger = logging.getLogger(__name__)

class Ui_UpdateCheckDialog(object):
    def setupUi(self, UpdateAvailableDialog):
        UpdateAvailableDialog.setObjectName("UpdateAvailableDialog")
        UpdateAvailableDialog.resize(594, 300)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/creepy/logo"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UpdateAvailableDialog.setWindowIcon(icon)
        self.buttonBox = QtWidgets.QDialogButtonBox(UpdateAvailableDialog)
        self.buttonBox.setGeometry(QtCore.QRect(240, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(UpdateAvailableDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 571, 221))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.versionsTableWidget = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        self.versionsTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.versionsTableWidget.setTabKeyNavigation(False)
        self.versionsTableWidget.setProperty("showDropIndicator", False)
        self.versionsTableWidget.setRowCount(1)
        self.versionsTableWidget.setColumnCount(4)
        self.versionsTableWidget.setObjectName("versionsTableWidget")
        
        # Set headers for the table
        self.versionsTableWidget.setHorizontalHeaderLabels(["Component", "Current Version", "Latest Version", "Status"])
        
        # Set up item for demonstration
        item = QtWidgets.QTableWidgetItem("CreepyAI")
        self.versionsTableWidget.setItem(0, 0, item)
        
        self.versionsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.versionsTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.versionsTableWidget)

        self.retranslateUi(UpdateAvailableDialog)
        self.buttonBox.accepted.connect(UpdateAvailableDialog.accept)
        self.buttonBox.rejected.connect(UpdateAvailableDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UpdateAvailableDialog)

    def retranslateUi(self, UpdateAvailableDialog):
        _translate = QtCore.QCoreApplication.translate
        UpdateAvailableDialog.setWindowTitle(_translate("UpdateAvailableDialog", "Update Check"))
        self.label.setText(_translate("UpdateAvailableDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Results of Update Check</span></p></body></html>"))

class UpdateCheckDialog(QDialog):
    """Dialog for checking for software updates"""
    
    def __init__(self, parent=None, current_version="2.5.0"):
        QDialog.__init__(self, parent)
        self.ui = Ui_UpdateCheckDialog()
        self.ui.setupUi(self)
        self.current_version = current_version
        
        # Connect signals
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        # Check for updates when dialog opens
        self.check_for_updates()
        
    def check_for_updates(self):
        """Check for updates from the CreepyAI server"""
        try:
            self.ui.versionsTableWidget.clearContents()
            self.ui.versionsTableWidget.setRowCount(3)  # Core + 2 key plugins
            
            # Add current version information
            self.ui.versionsTableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("CreepyAI Core"))
            self.ui.versionsTableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.current_version))
            
            # Add plugin information
            self.ui.versionsTableWidget.setItem(1, 0, QtWidgets.QTableWidgetItem("Social Media Plugins"))
            self.ui.versionsTableWidget.setItem(1, 1, QtWidgets.QTableWidgetItem("1.3.2"))
            
            self.ui.versionsTableWidget.setItem(2, 0, QtWidgets.QTableWidgetItem("Export Plugins"))
            self.ui.versionsTableWidget.setItem(2, 1, QtWidgets.QTableWidgetItem("1.2.0"))
            
            # Make API request for latest versions
            try:
                response = requests.get("https://api.github.com/repos/jkakavas/creepy/releases/latest", timeout=5)
                if response.status_code == 200:
                    release_data = response.json()
                    latest_version = release_data.get("tag_name", "0.0.0").lstrip("v")
                    
                    # Compare versions
                    self.ui.versionsTableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(latest_version))
                    
                    if version.parse(latest_version) > version.parse(self.current_version):
                        status_item = QtWidgets.QTableWidgetItem("Update Available")
                        status_item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                        self.ui.versionsTableWidget.setItem(0, 3, status_item)
                    else:
                        status_item = QtWidgets.QTableWidgetItem("Up to date")
                        status_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 128, 0)))
                        self.ui.versionsTableWidget.setItem(0, 3, status_item)
                else:
                    self.ui.versionsTableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem("Check failed"))
                    self.ui.versionsTableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(f"Error: {response.status_code}"))
                
                # Mock plugin update data (in a real app, this would come from a server)
                self.ui.versionsTableWidget.setItem(1, 2, QtWidgets.QTableWidgetItem("1.4.0"))
                status_item = QtWidgets.QTableWidgetItem("Update Available")
                status_item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                self.ui.versionsTableWidget.setItem(1, 3, status_item)
                
                self.ui.versionsTableWidget.setItem(2, 2, QtWidgets.QTableWidgetItem("1.2.0"))
                status_item = QtWidgets.QTableWidgetItem("Up to date")
                status_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 128, 0)))
                self.ui.versionsTableWidget.setItem(2, 3, status_item)
                
            except Exception as e:
                logger.error(f"Failed to check for updates: {str(e)}")
                self.ui.versionsTableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem("Error"))
                self.ui.versionsTableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(f"Check failed: {str(e)}"))
                
                # Still show plugin rows but mark as check failed
                for row in range(1, 3):
                    self.ui.versionsTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem("Unknown"))
                    self.ui.versionsTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem("Check failed"))
            
            # Resize columns to content
            self.ui.versionsTableWidget.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error in update check: {str(e)}")
            QMessageBox.warning(self, "Update Check Failed", f"Failed to check for updates: {str(e)}")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    UpdateAvailableDialog = QtWidgets.QDialog()
    ui = Ui_UpdateCheckDialog()
    ui.setupUi(UpdateAvailableDialog)
    UpdateAvailableDialog.show()
    sys.exit(app.exec_())

