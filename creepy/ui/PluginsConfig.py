# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\pluginsConfig.ui'
#
# Created: Fri Jan 31 15:31:51 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = lambda s: s

class Ui_PluginsConfigurationDialog(object):
    def setupUi(self, PluginsConfigurationDialog):
        PluginsConfigurationDialog.setObjectName(_fromUtf8("PluginsConfigurationDialog"))
        PluginsConfigurationDialog.resize(810, 640)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PluginsConfigurationDialog.sizePolicy().hasHeightForWidth())
        PluginsConfigurationDialog.setSizePolicy(sizePolicy)
        PluginsConfigurationDialog.setMinimumSize(QtCore.QSize(810, 640))
        PluginsConfigurationDialog.setMaximumSize(QtCore.QSize(810, 640))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/properties")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        PluginsConfigurationDialog.setWindowIcon(icon)
        self.BtnBox = QtWidgets.QDialogButtonBox(PluginsConfigurationDialog)
        self.BtnBox.setGeometry(QtCore.QRect(430, 600, 341, 32))
        self.BtnBox.setOrientation(QtCore.Qt.Horizontal)
        self.BtnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnBox.setObjectName(_fromUtf8("BtnBox"))
        self.PluginsList = QtWidgets.QListView(PluginsConfigurationDialog)
        self.PluginsList.setGeometry(QtCore.QRect(10, 10, 211, 581))
        self.PluginsList.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.PluginsList.setObjectName(_fromUtf8("PluginsList"))

        self.retranslateUi(PluginsConfigurationDialog)
        QtCore.QObject.connect(self.BtnBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PluginsConfigurationDialog.accept)
        QtCore.QObject.connect(self.BtnBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PluginsConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PluginsConfigurationDialog)

    def retranslateUi(self, PluginsConfigurationDialog):
        PluginsConfigurationDialog.setWindowTitle(QtWidgets.QApplication.translate("PluginsConfigurationDialog", "Plugins Configuration", None))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PluginsConfigurationDialog = QtWidgets.QDialog()
    ui = Ui_PluginsConfigurationDialog()
    ui.setupUi(PluginsConfigurationDialog)
    PluginsConfigurationDialog.show()
    sys.exit(app.exec_())
