#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a template for UI files to be generated with PyQt5's designer.
You would normally auto-generate these files and not edit them manually.
"""
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SampleDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 361, 41))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Sample Dialog"))
        self.label.setText(_translate("Dialog", "This is a sample dialog template for CreepyAI"))

"""
Note: To create actual UI files, use Qt Designer and save as .ui files.
Then convert them to Python using:

pyuic5 -x input.ui -o output.py

You may want to create UI files for:
1. PersonProjectWizardUI.py
2. PluginsConfigurationDialogUI.py
3. FilterLocationsDateDialogUI.py
4. FilterLocationsPointDialogUI.py
5. AboutDialogUI.py
6. VerifyDeleteDialogUI.py
7. UpdateCheckDialogUI.py
"""
