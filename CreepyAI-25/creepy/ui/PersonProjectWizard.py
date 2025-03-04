# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\personProjectWizard.ui'
#
# Created: Fri Jan 31 15:30:24 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_personProjectWizard(object):
    def setupUi(self, personProjectWizard):
        personProjectWizard.setObjectName("personProjectWizard")
        personProjectWizard.resize(898, 702)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/creepy/user"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        personProjectWizard.setWindowIcon(icon)
        personProjectWizard.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        personProjectWizard.setOptions(QtWidgets.QWizard.HelpButtonOnRight)
        
        # Setup wizard pages
        self._setup_wizard_page_1(personProjectWizard)
        self._setup_wizard_page_2(personProjectWizard)
        self._setup_wizard_page_3(personProjectWizard)
        self._setup_wizard_page_4(personProjectWizard)

        self.retranslateUi(personProjectWizard)
        QtCore.QMetaObject.connectSlotsByName(personProjectWizard)

    def _setup_wizard_page_1(self, personProjectWizard):
        # Page 1 - Project Metadata
        self.personProjectWizardPage1 = QtWidgets.QWizardPage()
        self.personProjectWizardPage1.setObjectName("personProjectWizardPage1")
        self.gridLayoutWidget = QtWidgets.QWidget(self.personProjectWizardPage1)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 861, 591))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        
        # Setup form fields
        self.personProjectDescriptionValue = QtWidgets.QPlainTextEdit(self.gridLayoutWidget)
        self.personProjectDescriptionValue.setPlainText("")
        self.personProjectDescriptionValue.setObjectName("personProjectDescriptionValue")
        self.gridLayout_3.addWidget(self.personProjectDescriptionValue, 2, 1, 1, 1)
        
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 3, 1, 1, 1)
        
        self.personProjectNameValue = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.personProjectNameValue.setObjectName("personProjectNameValue")
        self.gridLayout_3.addWidget(self.personProjectNameValue, 0, 1, 1, 1)
        
        self.personProjectNameLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.personProjectNameLabel.setEnabled(True)
        self.personProjectNameLabel.setObjectName("personProjectNameLabel")
        self.gridLayout_3.addWidget(self.personProjectNameLabel, 0, 0, 1, 1)
        
        self.personProjectKeywordsValue = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.personProjectKeywordsValue.setObjectName("personProjectKeywordsValue")
        self.gridLayout_3.addWidget(self.personProjectKeywordsValue, 1, 1, 1, 1)
        
        self.personProjectDescriptionLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.personProjectDescriptionLabel.sizePolicy().hasHeightForWidth())
        self.personProjectDescriptionLabel.setSizePolicy(sizePolicy)
        self.personProjectDescriptionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.personProjectDescriptionLabel.setObjectName("personProjectDescriptionLabel")
        self.gridLayout_3.addWidget(self.personProjectDescriptionLabel, 2, 0, 1, 1)
        
        self.personProkectKeywordsLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.personProkectKeywordsLabel.setObjectName("personProkectKeywordsLabel")
        self.gridLayout_3.addWidget(self.personProkectKeywordsLabel, 1, 0, 1, 1)
        
        personProjectWizard.addPage(self.personProjectWizardPage1)

    def _setup_wizard_page_2(self, personProjectWizard):
        # Page 2 - Target Selection
        self.personProjectWizardPage2 = QtWidgets.QWizardPage()
        self.personProjectWizardPage2.setObjectName("personProjectWizardPage2")
        self.gridLayout = QtWidgets.QGridLayout(self.personProjectWizardPage2)
        self.gridLayout.setObjectName("gridLayout")
        
        # Create button layouts with helper method
        self.horizontalLayout = self._create_button_layout(self.personProjectWizardPage2, "btnAddTarget", "Add To Targets")
        self.gridLayout.addLayout(self.horizontalLayout, 5, 3, 1, 1)
        
        # Setup tables with consistent properties
        self.personProjectSelectedTargetsTable = self._create_table_view(
            self.personProjectWizardPage2, "personProjectSelectedTargetsTable", 
            drag_enabled=False, drop_mode=QtWidgets.QAbstractItemView.DropOnly,
            selection_mode=QtWidgets.QAbstractItemView.MultiSelection
        )
        self.gridLayout.addWidget(self.personProjectSelectedTargetsTable, 8, 2, 1, 2)
        
        self.personProjectTargetSeperatorLine = QtWidgets.QFrame(self.personProjectWizardPage2)
        self.personProjectTargetSeperatorLine.setLineWidth(4)
        self.personProjectTargetSeperatorLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.personProjectTargetSeperatorLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.personProjectTargetSeperatorLine.setObjectName("personProjectTargetSeperatorLine")
        self.gridLayout.addWidget(self.personProjectTargetSeperatorLine, 6, 1, 1, 3)
        
        self.personProjectSearchResultsTable = self._create_table_view(
            self.personProjectWizardPage2, "personProjectSearchResultsTable", 
            drag_enabled=True, drop_mode=QtWidgets.QAbstractItemView.DragDrop
        )
        self.gridLayout.addWidget(self.personProjectSearchResultsTable, 4, 2, 1, 2)
        
        # Add labels
        self._add_label(self.personProjectWizardPage2, "personProjectSearchForLabel", 
                        self.gridLayout, 0, 0, 1, 2)
        self._add_label(self.personProjectWizardPage2, "personProjectSearchResultsLabel", 
                        self.gridLayout, 4, 0, 1, 1)
        self._add_label(self.personProjectWizardPage2, "personProjectSelectedTargetsLabel", 
                        self.gridLayout, 8, 0, 1, 1)
        self._add_label(self.personProjectWizardPage2, "personProjectSearchInLabel", 
                        self.gridLayout, 1, 0, 1, 2)
        
        # Add spacers
        self.gridLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, 
                                                      QtWidgets.QSizePolicy.Minimum), 3, 2, 1, 1)
        
        # Details label
        self.personProjectSearchForDetailsLabel = QtWidgets.QLabel(self.personProjectWizardPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.personProjectSearchForDetailsLabel.sizePolicy().hasHeightForWidth())
        self.personProjectSearchForDetailsLabel.setSizePolicy(sizePolicy)
        self.personProjectSearchForDetailsLabel.setObjectName("personProjectSearchForDetailsLabel")
        self.gridLayout.addWidget(self.personProjectSearchForDetailsLabel, 0, 3, 1, 1)
        
        # Plugins area
        self.personProjectAvailablePluginsScrollArea = QtWidgets.QScrollArea(self.personProjectWizardPage2)
        self.personProjectAvailablePluginsScrollArea.setWidgetResizable(True)
        self.personProjectAvailablePluginsScrollArea.setObjectName("personProjectAvailablePluginsScrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 98, 91))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.personProjectAvailablePluginsListView = QtWidgets.QListView(self.scrollAreaWidgetContents)
        self.personProjectAvailablePluginsListView.setObjectName("personProjectAvailablePluginsListView")
        self.verticalLayout.addWidget(self.personProjectAvailablePluginsListView)
        self.personProjectAvailablePluginsScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.personProjectAvailablePluginsScrollArea, 1, 2, 1, 2)
        
        # Search field
        self.personProjectSearchForValue = QtWidgets.QLineEdit(self.personProjectWizardPage2)
        self.personProjectSearchForValue.setObjectName("personProjectSearchForValue")
        self.gridLayout.addWidget(self.personProjectSearchForValue, 0, 2, 1, 1)
        
        # Search button layout
        self.horizontalLayout_2 = self._create_button_layout(
            self.personProjectWizardPage2, "personProjectSearchButton", "Search", is_default=True
        )
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 3, 1, 1)
        
        # More spacers
        self.gridLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, 
                                                     QtWidgets.QSizePolicy.Minimum), 5, 2, 1, 1)
        self.gridLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, 
                                                     QtWidgets.QSizePolicy.Minimum), 9, 2, 1, 1)
        
        # Remove button layout
        self.horizontalLayout_3 = self._create_button_layout(
            self.personProjectWizardPage2, "btnRemoveTarget", "Remove Selected"
        )
        self.gridLayout.addLayout(self.horizontalLayout_3, 9, 3, 1, 1)
        
        personProjectWizard.addPage(self.personProjectWizardPage2)

    def _setup_wizard_page_3(self, personProjectWizard):
        # Page 3 - Parameters
        self.personProjectWizardPage3 = QtWidgets.QWizardPage()
        self.personProjectWizardPage3.setObjectName("personProjectWizardPage3")
        self.personProjectWizardSearchConfigPluginsList = QtWidgets.QListView(self.personProjectWizardPage3)
        self.personProjectWizardSearchConfigPluginsList.setGeometry(QtCore.QRect(0, 0, 256, 531))
        self.personProjectWizardSearchConfigPluginsList.setObjectName("personProjectWizardSearchConfigPluginsList")
        self.searchConfiguration = QtWidgets.QStackedWidget(self.personProjectWizardPage3)
        self.searchConfiguration.setGeometry(QtCore.QRect(260, 0, 591, 531))
        self.searchConfiguration.setObjectName("searchConfiguration")
        personProjectWizard.addPage(self.personProjectWizardPage3)

    def _setup_wizard_page_4(self, personProjectWizard):
        # Page 4 - Finalization
        self.personProjectWizardPage4 = QtWidgets.QWizardPage()
        self.personProjectWizardPage4.setObjectName("personProjectWizardPage4")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.personProjectWizardPage4)
        self.gridLayout_2.setObjectName("gridLayout_2")
        personProjectWizard.addPage(self.personProjectWizardPage4)
    
    # Helper methods to reduce redundancy
    def _create_table_view(self, parent, object_name, drag_enabled=False, drop_mode=None, selection_mode=None):
        table = QtWidgets.QTableView(parent)
        table.setDragEnabled(drag_enabled)
        table.setDragDropOverwriteMode(True)
        if drop_mode:
            table.setDragDropMode(drop_mode)
        if drop_mode == QtWidgets.QAbstractItemView.DropOnly:
            table.setDefaultDropAction(QtCore.Qt.CopyAction)
        if selection_mode:
            table.setSelectionMode(selection_mode)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSortingEnabled(True)
        table.setObjectName(object_name)
        
        # Common header settings
        table.horizontalHeader().setCascadingSectionResizes(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setCascadingSectionResizes(True)
        
        return table
    
    def _create_button_layout(self, parent, btn_name, btn_text, is_default=False):
        layout = QtWidgets.QHBoxLayout()
        layout.setObjectName(btn_name + "_layout")
        
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, 
                                      QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        
        button = QtWidgets.QPushButton(parent)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.setStyleSheet("")
        button.setObjectName(btn_name)
        if is_default:
            button.setDefault(True)
        layout.addWidget(button)
        
        # Store button reference for translation
        setattr(self, btn_name, button)
        
        return layout
    
    def _add_label(self, parent, object_name, layout, row, col, rowspan=1, colspan=1):
        label = QtWidgets.QLabel(parent)
        label.setObjectName(object_name)
        layout.addWidget(label, row, col, rowspan, colspan)
        setattr(self, object_name, label)

    def retranslateUi(self, personProjectWizard):
        personProjectWizard.setWindowTitle(QtWidgets.QApplication.translate("personProjectWizard", "New Person Project", None))
        self.personProjectWizardPage1.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 1 - Set Project Metadata", None))
        self.personProjectWizardPage1.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Add project related information", None))
        self.personProjectNameValue.setPlaceholderText(QtWidgets.QApplication.translate("personProjectWizard", "Add a name for your project", None))
        self.personProjectNameLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Project Name ", None))
        self.personProjectKeywordsValue.setPlaceholderText(QtWidgets.QApplication.translate("personProjectWizard", "Add comma seperated keywords for your project", None))
        self.personProjectDescriptionLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Description", None))
        self.personProkectKeywordsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Keywords", None))
        self.personProjectWizardPage2.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 2 - Set the target", None))
        self.personProjectWizardPage2.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Search for the person you want to track using the available plugins and add it to the <font color=\"red\">selected targets</font> by drag and drop or by clicking \"Add To Targets\"", None))
        self.btnAddTarget.setText(QtWidgets.QApplication.translate("personProjectWizard", "Add To Targets", None))
        self.personProjectSearchForLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600;\">Search for</span></p></body></html>", None))
        self.personProjectSearchResultsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600;\">Search Results </span></p></body></html>", None))
        self.personProjectSelectedTargetsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">Selected Targets</span></p></body></html>", None))
        self.personProjectSearchInLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600;\">Search In</span></p></body></html>", None))
        self.personProjectSearchForDetailsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Search by username, mail, full name, id", None))
        self.personProjectSearchButton.setToolTip(QtWidgets.QApplication.translate("personProjectWizard", "Search for targets in the selected plugins", None))
        self.personProjectSearchButton.setText(QtWidgets.QApplication.translate("personProjectWizard", "Search", None))
        self.btnRemoveTarget.setText(QtWidgets.QApplication.translate("personProjectWizard", "Remove Selected", None))
        self.personProjectWizardPage3.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 3 - Set Parameters", None))
        self.personProjectWizardPage3.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Provide the necessary search parameters for the plugins you are using", None))
        self.personProjectWizardPage4.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 4  - Finalize Project", None))
        self.personProjectWizardPage4.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Click Finish to save the Project Configuration ", None))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    personProjectWizard = QtWidgets.QWizard()
    ui = Ui_personProjectWizard()
    ui.setupUi(personProjectWizard)
    personProjectWizard.show()
    sys.exit(app.exec_())

