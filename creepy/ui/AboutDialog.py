<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class AboutDialog(QDialog):
    """About dialog for the CreepyAI application."""
    
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        
        self.setWindowTitle("About CreepyAI")
        self.setFixedSize(400, 400)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = Icons.get_pixmap("logo")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # App name
        app_name = QLabel("CreepyAI")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        app_name.setFont(font)
        app_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description = QLabel(
            "<p>CreepyAI is a geolocation intelligence tool that collects and analyzes "
            "social media and online data to track and visualize user locations "
            "without relying on APIs.</p>"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Credits
        credits = QLabel(
            "<p><b>Created by:</b> CreepyAI Team</p>"
            "<p><b>License:</b> See LICENSE file</p>"
        )
        credits.setWordWrap(True)
        credits.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits)
        
        # Disclaimer
        disclaimer = QLabel(
            "<p><small>This software is provided for educational and research purposes only. "
            "Users are responsible for using this tool in an ethical and legal manner.</small></p>"
        )
        disclaimer.setWordWrap(True)
        disclaimer.setAlignment(Qt.AlignCenter)
        layout.addWidget(disclaimer)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
=======
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
>>>>>>> gs-ai-patch-1
