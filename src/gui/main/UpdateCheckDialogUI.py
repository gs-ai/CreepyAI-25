#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_updateCheckDialog(object):
    def setupUi(self, updateCheckDialog):
        updateCheckDialog.setObjectName("updateCheckDialog")
        updateCheckDialog.resize(600, 350)
        
        # Set up the main layout
        self.verticalLayout = QtWidgets.QVBoxLayout(updateCheckDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Header label
        self.headerLabel = QtWidgets.QLabel(updateCheckDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.headerLabel.setFont(font)
        self.headerLabel.setObjectName("headerLabel")
        self.verticalLayout.addWidget(self.headerLabel)
        
        # Status message label
        self.statusLabel = QtWidgets.QLabel(updateCheckDialog)
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)
        
        # Table widget for versions
        self.versionsTableWidget = QtWidgets.QTableWidget(updateCheckDialog)
        self.versionsTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.versionsTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.versionsTableWidget.setObjectName("versionsTableWidget")
        self.versionsTableWidget.setColumnCount(4)
        self.versionsTableWidget.setRowCount(0)
        
        # Set header labels
        item = QtWidgets.QTableWidgetItem()
        self.versionsTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.versionsTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.versionsTableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.versionsTableWidget.setHorizontalHeaderItem(3, item)
        
        # Configure table properties
        self.versionsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.versionsTableWidget.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.versionsTableWidget)
        
        # Notes label
        self.notesLabel = QtWidgets.QLabel(updateCheckDialog)
        self.notesLabel.setObjectName("notesLabel")
        self.verticalLayout.addWidget(self.notesLabel)
        
        # Progress bar
        self.progressBar = QtWidgets.QProgressBar(updateCheckDialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        
        # Button box
        self.buttonBox = QtWidgets.QDialogButtonBox(updateCheckDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        
        # Connect signals
        self.buttonBox.accepted.connect(updateCheckDialog.accept)
        self.buttonBox.rejected.connect(updateCheckDialog.reject)
        
        self.retranslateUi(updateCheckDialog)
        QtCore.QMetaObject.connectSlotsByName(updateCheckDialog)

    def retranslateUi(self, updateCheckDialog):
        _translate = QtCore.QCoreApplication.translate
        updateCheckDialog.setWindowTitle(_translate("updateCheckDialog", "Check for Updates"))
        self.headerLabel.setText(_translate("updateCheckDialog", "Check for Updates"))
        self.statusLabel.setText(_translate("updateCheckDialog", "Checking for updates..."))
        
        # Set table headers
        self.versionsTableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem(_translate("updateCheckDialog", "Component")))
        self.versionsTableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem(_translate("updateCheckDialog", "Current Version")))
        self.versionsTableWidget.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem(_translate("updateCheckDialog", "Latest Version")))
        self.versionsTableWidget.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem(_translate("updateCheckDialog", "Status")))
        
        self.notesLabel.setText(_translate("updateCheckDialog", ""))
