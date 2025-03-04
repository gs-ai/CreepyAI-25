<<<<<<< HEAD
#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from creepy.resources.icons import Icons
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
        icon.addPixmap(Icons.get_pixmap("logo"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
=======
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\updateCheckDialog.ui'
#
# Created: Wed Jan 08 19:47:23 2014
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_UpdateAvailableDialog(object):
    def setupUi(self, UpdateAvailableDialog):
        UpdateAvailableDialog.setObjectName(_fromUtf8("UpdateAvailableDialog"))
        UpdateAvailableDialog.resize(594, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/cr/Eye_of_Sauron_by_Blood_Solice.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UpdateAvailableDialog.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(UpdateAvailableDialog)
        self.buttonBox.setGeometry(QtCore.QRect(240, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtGui.QWidget(UpdateAvailableDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 571, 221))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.versionsTableWidget = QtGui.QTableWidget(self.verticalLayoutWidget)
        self.versionsTableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
>>>>>>> gs-ai-patch-1
        self.versionsTableWidget.setTabKeyNavigation(False)
        self.versionsTableWidget.setProperty("showDropIndicator", False)
        self.versionsTableWidget.setRowCount(1)
        self.versionsTableWidget.setColumnCount(4)
<<<<<<< HEAD
        self.versionsTableWidget.setObjectName("versionsTableWidget")
        
        # Set headers for the table
        self.versionsTableWidget.setHorizontalHeaderLabels(["Component", "Current Version", "Latest Version", "Status"])
        
        # Set up item for demonstration
        item = QtWidgets.QTableWidgetItem("CreepyAI")
        self.versionsTableWidget.setItem(0, 0, item)
        
=======
        self.versionsTableWidget.setObjectName(_fromUtf8("versionsTableWidget"))
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 1, item)
        item = QtGui.QTableWidgetItem()
        self.versionsTableWidget.setItem(0, 2, item)
>>>>>>> gs-ai-patch-1
        self.versionsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.versionsTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.versionsTableWidget)

        self.retranslateUi(UpdateAvailableDialog)
<<<<<<< HEAD
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
=======
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UpdateAvailableDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UpdateAvailableDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UpdateAvailableDialog)

    def retranslateUi(self, UpdateAvailableDialog):
        UpdateAvailableDialog.setWindowTitle(QtGui.QApplication.translate("UpdateAvailableDialog", "Update Check", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("UpdateAvailableDialog", "<html><head/><body><p><span style=\" font-weight:600;\">Results of Update Check</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.versionsTableWidget.isSortingEnabled()
        self.versionsTableWidget.setSortingEnabled(False)
        self.versionsTableWidget.setSortingEnabled(__sortingEnabled)

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    UpdateAvailableDialog = QtGui.QDialog()
    ui = Ui_UpdateAvailableDialog()
>>>>>>> gs-ai-patch-1
    ui.setupUi(UpdateAvailableDialog)
    UpdateAvailableDialog.show()
    sys.exit(app.exec_())

