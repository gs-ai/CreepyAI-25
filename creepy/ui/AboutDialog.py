# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\aboutDialog.ui'
#
# Created: Fri Jan 31 15:29:04 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        aboutDialog.setObjectName(_fromUtf8("aboutDialog"))
        aboutDialog.resize(394, 338)
        aboutDialog.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/creepy")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        aboutDialog.setWindowIcon(icon)
        aboutDialog.setModal(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(aboutDialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 290, 361, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtWidgets.QWidget(aboutDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 361, 281))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(aboutDialog)
        QtCore.QMetaObject.connectSlotsByName(aboutDialog)

    def retranslateUi(self, aboutDialog):
        aboutDialog.setWindowTitle(QtWidgets.QApplication.translate("aboutDialog", "About", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("aboutDialog", "<html><head/><body><p align=\"center\"><img src=\":/cr/creepy32.png\"/></p><p><br/></p><p align=\"center\"><span style=\" font-size:9pt;\">Creepy is a geolocation OSINT tool. </span></p><p><br/></p><p><span style=\" font-weight:600;\">Version : </span>1.0 - Codename &quot;<span style=\" font-style:italic;\">Diskbråck</span>&quot;</p><p><span style=\" font-weight:600;\">Author</span> : Ioannis Kakavas &lt; jkakavas@gmail.com &gt;</p><p><span style=\" font-weight:600;\">Website</span>: www.geocreepy.net</p></body></html>", None, -1))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    aboutDialog = QtWidgets.QDialog()
    ui = Ui_aboutDialog()
    ui.setupUi(aboutDialog)
    aboutDialog.show()
    sys.exit(app.exec_())
