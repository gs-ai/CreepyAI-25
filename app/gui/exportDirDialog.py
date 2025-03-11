from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ExportDirDialog(object):
    def setupUi(self, ExportDirDialog):
        ExportDirDialog.setObjectName("ExportDirDialog")
        ExportDirDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ExportDirDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblExportDir = QtWidgets.QLabel(ExportDirDialog)
        self.lblExportDir.setObjectName("lblExportDir")
        self.verticalLayout.addWidget(self.lblExportDir)
        self.lineEditExportDir = QtWidgets.QLineEdit(ExportDirDialog)
        self.lineEditExportDir.setObjectName("lineEditExportDir")
        self.verticalLayout.addWidget(self.lineEditExportDir)
        self.btnBrowse = QtWidgets.QPushButton(ExportDirDialog)
        self.btnBrowse.setObjectName("btnBrowse")
        self.verticalLayout.addWidget(self.btnBrowse)
        self.btnExport = QtWidgets.QPushButton(ExportDirDialog)
        self.btnExport.setObjectName("btnExport")
        self.verticalLayout.addWidget(self.btnExport)
        self.btnCancel = QtWidgets.QPushButton(ExportDirDialog)
        self.btnCancel.setObjectName("btnCancel")
        self.verticalLayout.addWidget(self.btnCancel)

        self.retranslateUi(ExportDirDialog)
        QtCore.QMetaObject.connectSlotsByName(ExportDirDialog)

    def retranslateUi(self, ExportDirDialog):
        _translate = QtCore.QCoreApplication.translate
        ExportDirDialog.setWindowTitle(_translate("ExportDirDialog", "Export Directory"))
        self.lblExportDir.setText(_translate("ExportDirDialog", "Select Export Directory"))
        self.btnBrowse.setText(_translate("ExportDirDialog", "Browse"))
        self.btnExport.setText(_translate("ExportDirDialog", "Export"))
        self.btnCancel.setText(_translate("ExportDirDialog", "Cancel"))

class ExportDirDialogApp(QtWidgets.QDialog, Ui_ExportDirDialog):
    def __init__(self, parent=None):
        super(ExportDirDialogApp, self).__init__(parent)
        self.setupUi(self)
        self.btnBrowse.clicked.connect(self.browse_clicked)
        self.btnExport.clicked.connect(self.export_clicked)
        self.btnCancel.clicked.connect(self.cancel_clicked)

    def browse_clicked(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.lineEditExportDir.setText(directory)

    def export_clicked(self):
        export_dir = self.lineEditExportDir.text()
        if export_dir:
            print(f"Exporting to directory: {export_dir}")
            # Add logic to export data to the selected directory
            self.accept()

    def cancel_clicked(self):
        self.reject()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = ExportDirDialogApp()
    dialog.show()
    sys.exit(app.exec_())
