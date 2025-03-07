#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VerifyDeleteDialog(object):
    def setupUi(self, VerifyDeleteDialog):
        VerifyDeleteDialog.setObjectName("VerifyDeleteDialog")
        VerifyDeleteDialog.resize(450, 250)
        
        # Create main layout
        self.verticalLayout = QtWidgets.QVBoxLayout(VerifyDeleteDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Create header layout
        self.headerLayout = QtWidgets.QHBoxLayout()
        self.headerLayout.setObjectName("headerLayout")
        
        # Warning icon
        self.warningIcon = QtWidgets.QLabel(VerifyDeleteDialog)
        self.warningIcon.setMinimumSize(QtCore.QSize(48, 48))
        self.warningIcon.setMaximumSize(QtCore.QSize(48, 48))
        self.warningIcon.setText("")
        self.warningIcon.setObjectName("warningIcon")
        self.headerLayout.addWidget(self.warningIcon)
        
        # Warning text
        self.warningText = QtWidgets.QLabel(VerifyDeleteDialog)
        self.warningText.setWordWrap(True)
        self.warningText.setTextFormat(QtCore.Qt.RichText)
        self.warningText.setObjectName("warningText")
        self.headerLayout.addWidget(self.warningText)
        
        # Add header layout to main layout
        self.verticalLayout.addLayout(self.headerLayout)
        
        # Add spacer
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        # Confirmation checkbox
        self.confirmCheckBox = QtWidgets.QCheckBox(VerifyDeleteDialog)
        self.confirmCheckBox.setObjectName("confirmCheckBox")
        self.verticalLayout.addWidget(self.confirmCheckBox)
        
        # Add button box
        self.buttonBox = QtWidgets.QDialogButtonBox(VerifyDeleteDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        
        # Connect signals
        self.buttonBox.accepted.connect(VerifyDeleteDialog.accept)
        self.buttonBox.rejected.connect(VerifyDeleteDialog.reject)
        
        self.retranslateUi(VerifyDeleteDialog)
        QtCore.QMetaObject.connectSlotsByName(VerifyDeleteDialog)

    def retranslateUi(self, VerifyDeleteDialog):
        _translate = QtCore.QCoreApplication.translate
        VerifyDeleteDialog.setWindowTitle(_translate("VerifyDeleteDialog", "Confirm Deletion"))
        self.warningText.setText(_translate("VerifyDeleteDialog", "<p>Are you sure you want to delete this item?</p><p>This action cannot be undone.</p>"))
        self.confirmCheckBox.setText(_translate("VerifyDeleteDialog", "Yes, I want to permanently delete this item"))
