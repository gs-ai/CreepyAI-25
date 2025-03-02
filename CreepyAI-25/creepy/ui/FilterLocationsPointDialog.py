# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\filterLocationsPointDialog.ui'
#
# Created: Fri Jan 31 15:33:25 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

try:
    _fromUtf8 = lambda s: s
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FilteLocationsPointDialog(object):
    def setupUi(self, FilteLocationsPointDialog):
        FilteLocationsPointDialog.setObjectName(_fromUtf8("FilteLocationsPointDialog"))
        FilteLocationsPointDialog.resize(758, 565)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/marker")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FilteLocationsPointDialog.setWindowIcon(icon)
        self.buttonBox = QtWidgets.QDialogButtonBox(FilteLocationsPointDialog)
        self.buttonBox.setGeometry(QtCore.QRect(390, 520, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtWidgets.QWidget(FilteLocationsPointDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 731, 501))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.containerLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setTextFormat(QtCore.Qt.RichText)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.webView = QtWebEngineWidgets.QWebEngineView(self.verticalLayoutWidget)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.containerLayout.addWidget(self.webView)
        self.controlsContainerLayout = QtWidgets.QHBoxLayout()
        self.controlsContainerLayout.setObjectName(_fromUtf8("controlsContainerLayout"))
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.controlsContainerLayout.addItem(spacerItem)
        self.radiusLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiusLabel.sizePolicy().hasHeightForWidth())
        self.radiusLabel.setSizePolicy(sizePolicy)
        self.radiusLabel.setTextFormat(QtCore.Qt.RichText)
        self.radiusLabel.setObjectName(_fromUtf8("radiusLabel"))
        self.controlsContainerLayout.addWidget(self.radiusLabel)
        self.radiusSpinBox = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiusSpinBox.sizePolicy().hasHeightForWidth())
        self.radiusSpinBox.setSizePolicy(sizePolicy)
        self.radiusSpinBox.setMaximum(1000)
        self.radiusSpinBox.setObjectName(_fromUtf8("radiusSpinBox"))
        self.controlsContainerLayout.addWidget(self.radiusSpinBox)
        self.radiusUnitComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiusUnitComboBox.sizePolicy().hasHeightForWidth())
        self.radiusUnitComboBox.setSizePolicy(sizePolicy)
        self.radiusUnitComboBox.setObjectName(_fromUtf8("radiusUnitComboBox"))
        self.controlsContainerLayout.addWidget(self.radiusUnitComboBox)
        self.containerLayout.addLayout(self.controlsContainerLayout)

        self.retranslateUi(FilteLocationsPointDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FilteLocationsPointDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FilteLocationsPointDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FilteLocationsPointDialog)

    def retranslateUi(self, FilteLocationsPointDialog):
        FilteLocationsPointDialog.setWindowTitle(QtWidgets.QApplication.translate("FilteLocationsPointDialog", "Filter Locations By Place", None))
        self.titleLabel.setText(QtWidgets.QApplication.translate("FilteLocationsPointDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Drop a </span><span style=\" font-size:9pt; font-weight:600; color:#ff0000;\">pin</span><span style=\" font-size:9pt;\"> on the map for your point of interest</span></p></body></html>", None))
        self.radiusLabel.setText(QtWidgets.QApplication.translate("FilteLocationsPointDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Distance from the POI :</span></p></body></html>", None))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FilteLocationsPointDialog = QtWidgets.QDialog()
    ui = Ui_FilteLocationsPointDialog()
    ui.setupUi(FilteLocationsPointDialog)
    FilteLocationsPointDialog.show()
    sys.exit(app.exec_())
