# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\filterLocationsDateDialog.ui'
#
# Created: Fri Jan 31 15:33:14 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FilterLocationsDateDialog(object):
    def setupUi(self, FilterLocationsDateDialog):
        FilterLocationsDateDialog.setObjectName(_fromUtf8("FilterLocationsDateDialog"))
        FilterLocationsDateDialog.resize(575, 403)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/calendar")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FilterLocationsDateDialog.setWindowIcon(icon)
        FilterLocationsDateDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterLocationsDateDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.containerLayout = QtWidgets.QVBoxLayout()
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtWidgets.QLabel(FilterLocationsDateDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.calendarContainerLayout = QtWidgets.QHBoxLayout()
        self.calendarContainerLayout.setObjectName(_fromUtf8("calendarContainerLayout"))
        self.startDateContainer = QtWidgets.QVBoxLayout()
        self.startDateContainer.setObjectName(_fromUtf8("startDateContainer"))
        self.startDateLabel = QtWidgets.QLabel(FilterLocationsDateDialog)
        self.startDateLabel.setTextFormat(QtCore.Qt.AutoText)
        self.startDateLabel.setObjectName(_fromUtf8("startDateLabel"))
        self.startDateContainer.addWidget(self.startDateLabel)
        self.stardateCalendarWidget = QtWidgets.QCalendarWidget(FilterLocationsDateDialog)
        self.stardateCalendarWidget.setObjectName(_fromUtf8("stardateCalendarWidget"))
        self.startDateContainer.addWidget(self.stardateCalendarWidget)
        self.calendarContainerLayout.addLayout(self.startDateContainer)
        self.endDateContainer = QtWidgets.QVBoxLayout()
        self.endDateContainer.setObjectName(_fromUtf8("endDateContainer"))
        self.endDateLabel = QtWidgets.QLabel(FilterLocationsDateDialog)
        self.endDateLabel.setObjectName(_fromUtf8("endDateLabel"))
        self.endDateContainer.addWidget(self.endDateLabel)
        self.endDateCalendarWidget = QtWidgets.QCalendarWidget(FilterLocationsDateDialog)
        self.endDateCalendarWidget.setObjectName(_fromUtf8("endDateCalendarWidget"))
        self.endDateContainer.addWidget(self.endDateCalendarWidget)
        self.calendarContainerLayout.addLayout(self.endDateContainer)
        self.containerLayout.addLayout(self.calendarContainerLayout)
        self.timeContainerLayout = QtWidgets.QHBoxLayout()
        self.timeContainerLayout.setObjectName(_fromUtf8("timeContainerLayout"))
        self.startDateTimeEdit = QtWidgets.QTimeEdit(FilterLocationsDateDialog)
        self.startDateTimeEdit.setObjectName(_fromUtf8("startDateTimeEdit"))
        self.timeContainerLayout.addWidget(self.startDateTimeEdit)
        self.endDateTimeEdit = QtWidgets.QTimeEdit(FilterLocationsDateDialog)
        self.endDateTimeEdit.setObjectName(_fromUtf8("endDateTimeEdit"))
        self.timeContainerLayout.addWidget(self.endDateTimeEdit)
        self.containerLayout.addLayout(self.timeContainerLayout)
        self.verticalLayout.addLayout(self.containerLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(FilterLocationsDateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FilterLocationsDateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FilterLocationsDateDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FilterLocationsDateDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FilterLocationsDateDialog)

    def retranslateUi(self, FilterLocationsDateDialog):
        FilterLocationsDateDialog.setWindowTitle(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "Filter Locations By Date", None, -1))
        self.titleLabel.setText(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Select the start and end dates and times</span></p></body></html>", None, -1))
        self.startDateLabel.setText(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "<b>Start Date</b>", None, -1))
        self.endDateLabel.setText(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "<b>End Date</b>", None, -1))
        self.startDateTimeEdit.setDisplayFormat(QtWidgets.QApplication.translate("FilterLocationsDateDialog", "hh:mm:ss AP", None, -1))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FilterLocationsDateDialog = QtWidgets.QDialog()
    ui = Ui_FilterLocationsDateDialog()
    ui.setupUi(FilterLocationsDateDialog)
    FilterLocationsDateDialog.show()
    sys.exit(app.exec_())
