"""
About dialog for CreepyAI
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblAbout = QtWidgets.QLabel(AboutDialog)
        self.lblAbout.setObjectName("lblAbout")
        self.verticalLayout.addWidget(self.lblAbout)
        self.btnClose = QtWidgets.QPushButton(AboutDialog)
        self.btnClose.setObjectName("btnClose")
        self.verticalLayout.addWidget(self.btnClose)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About CreepyAI"))
        self.lblAbout.setText(_translate("AboutDialog", "CreepyAI Version 1.0.0"))
        self.btnClose.setText(_translate("AboutDialog", "Close"))

class AboutDialogApp(QtWidgets.QDialog, Ui_AboutDialog):
    def __init__(self, parent=None):
        super(AboutDialogApp, self).__init__(parent)
        self.setupUi(self)
        self.btnClose.clicked.connect(self.close_clicked)

    def close_clicked(self):
        self.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = AboutDialogApp()
    dialog.show()
    sys.exit(app.exec_())
