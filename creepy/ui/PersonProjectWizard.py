<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from creepy.resources.icons import Icons
import logging
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QLineEdit, QTextEdit, QLabel, 
    QVBoxLayout, QHBoxLayout, QListWidget, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QFileDialog, QMessageBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

logger = logging.getLogger(__name__)

class PersonProjectWizard(QWizard):
    """Wizard for creating a new person-based OSINT project."""
    
    def __init__(self, plugin_manager, parent=None):
        super(PersonProjectWizard, self).__init__(parent)
        
        self.plugin_manager = plugin_manager
        self.project_data = {}
        
        # Configure wizard
        self.setWindowTitle("Create New Project")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(700, 500)
        
        # Add pages
        self.addPage(IntroPage())
        self.addPage(ProjectDetailsPage())
        self.addPage(TargetDetailsPage())
        self.addPage(PluginSelectionPage(plugin_manager))
        self.addPage(SummaryPage())
        
        logger.info("Project wizard initialized")
    
    def accept(self):
        """Process the collected data when the wizard is accepted."""
        # Get data from pages
        self.project_data = {
            "name": self.field("projectName"),
            "description": self.field("projectDescription"),
            "directory": self.field("projectDirectory"),
            "targets": [],
            "plugins": self.field("selectedPlugins"),
            "analyze_now": self.field("analyzeNow")
        }
        
        # Get target details from the target details page
        target_page = self.page(2)  # TargetDetailsPage is at index 2
        self.project_data["targets"] = target_page.get_targets()
        
        logger.info(f"Created new project: {self.project_data['name']}")
        super().accept()
    
    def get_project_data(self):
        """Get the collected project data."""
        return self.project_data


class IntroPage(QWizardPage):
    """Introduction page for the project wizard."""
    
    def __init__(self, parent=None):
        super(IntroPage, self).__init__(parent)
        
        self.setTitle("Introduction")
        self.setSubTitle("This wizard will help you create a new OSINT geolocation project.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add description label
        intro_text = """
        <p>CreepyAI helps you collect and analyze geolocation data for OSINT investigations without using APIs.</p>
        
        <p>You will be guided through the following steps:</p>
        <ol>
            <li>Enter basic project details</li>
            <li>Define target information</li>
            <li>Select data collection plugins</li>
            <li>Review and create the project</li>
        </ol>
        
        <p>Click Next to begin.</p>
        """
        
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)
        
        # Add spacer
        layout.addStretch()
        
        self.setLayout(layout)


class ProjectDetailsPage(QWizardPage):
    """Page for collecting project details."""
    
    def __init__(self, parent=None):
        super(ProjectDetailsPage, self).__init__(parent)
        
        self.setTitle("Project Details")
        self.setSubTitle("Enter basic information about your project.")
        
        # Create layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Project name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My OSINT Project")
        form_layout.addRow("Project Name:", self.name_edit)
        self.registerField("projectName*", self.name_edit)  # Required field
        
        # Project description field
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter a description for your project...")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        self.registerField("projectDescription", self.description_edit, "plainText")
        
        # Project directory field
        dir_layout = QHBoxLayout()
        self.directory_edit = QLineEdit()
        self.directory_edit.setReadOnly(True)
        dir_layout.addWidget(self.directory_edit)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button)
        
        form_layout.addRow("Project Directory:", dir_layout)
        self.registerField("projectDirectory*", self.directory_edit)  # Required field
        
        layout.addLayout(form_layout)
        
        # Add spacer
        layout.addStretch()
        
        self.setLayout(layout)
    
    def browse_directory(self):
        """Open dialog to select project directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.directory_edit.setText(directory)


class TargetDetailsPage(QWizardPage):
    """Page for defining target information."""
    
    def __init__(self, parent=None):
        super(TargetDetailsPage, self).__init__(parent)
        
        self.setTitle("Target Information")
        self.setSubTitle("Enter information about the target(s) you want to investigate.")
        
        self.targets = []
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create form for entering target details
        target_group = QGroupBox("Add Target")
        target_form = QFormLayout()
        
        # Target name field
        self.name_edit = QLineEdit()
        target_form.addRow("Name:", self.name_edit)
        
        # Target usernames field
        self.username_edit = QLineEdit()
        target_form.addRow("Username:", self.username_edit)
        
        # Target additional information
        self.info_edit = QTextEdit()
        self.info_edit.setMaximumHeight(60)
        target_form.addRow("Additional Info:", self.info_edit)
        
        target_group.setLayout(target_form)
        layout.addWidget(target_group)
        
        # Add button
        self.add_button = QPushButton("Add Target")
        self.add_button.clicked.connect(self.add_target)
        layout.addWidget(self.add_button)
        
        # Target list
        target_list_group = QGroupBox("Added Targets")
        target_list_layout = QVBoxLayout()
        
        self.target_table = QTableWidget(0, 3)  # 3 columns: Name, Username, Actions
        self.target_table.setHorizontalHeaderLabels(["Name", "Username", "Actions"])
        self.target_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.target_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.target_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.target_table.setColumnWidth(2, 100)
        
        target_list_layout.addWidget(self.target_table)
        target_list_group.setLayout(target_list_layout)
        layout.addWidget(target_list_group)
        
        self.setLayout(layout)
    
    def add_target(self):
        """Add a target to the list."""
        name = self.name_edit.text().strip()
        username = self.username_edit.text().strip()
        info = self.info_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Missing Information", "Please enter a name for the target.")
            return
        
        # Add target to internal list
        target = {
            "name": name,
            "username": username,
            "info": info
        }
        self.targets.append(target)
        
        # Add target to table
        row = self.target_table.rowCount()
        self.target_table.insertRow(row)
        self.target_table.setItem(row, 0, QTableWidgetItem(name))
        self.target_table.setItem(row, 1, QTableWidgetItem(username))
        
        # Add remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_target(row))
        self.target_table.setCellWidget(row, 2, remove_button)
        
        # Clear form fields
        self.name_edit.clear()
        self.username_edit.clear()
        self.info_edit.clear()
        
        # Focus on name field
        self.name_edit.setFocus()
    
    def remove_target(self, row):
        """Remove a target from the list."""
        if 0 <= row < len(self.targets):
            del self.targets[row]
            self.target_table.removeRow(row)
            
            # Update removal buttons row index
            for i in range(self.target_table.rowCount()):
                button = self.target_table.cellWidget(i, 2)
                if button:
                    button.clicked.disconnect()
                    button.clicked.connect(lambda idx=i: self.remove_target(idx))
    
    def get_targets(self):
        """Get the list of targets."""
        return self.targets
    
    def validatePage(self):
        """Validate the page before proceeding."""
        if not self.targets:
            QMessageBox.warning(self, "No Targets", "Please add at least one target.")
            return False
        return True


class PluginSelectionPage(QWizardPage):
    """Page for selecting data collection plugins."""
    
    def __init__(self, plugin_manager, parent=None):
        super(PluginSelectionPage, self).__init__(parent)
        
        self.setTitle("Select Data Sources")
        self.setSubTitle("Choose which data sources to use for geolocation collection.")
        
        self.plugin_manager = plugin_manager
        self.selected_plugins = []
        
        # Create layout
        layout = QVBoxLayout()
        
        # Plugin list
        self.plugin_list = QListWidget()
        self.load_plugins()
        layout.addWidget(self.plugin_list)
        
        # Load plugins in list
        self.registerField("selectedPlugins", self)
        
        # Add analyze now checkbox
        self.analyze_now = QCheckBox("Analyze data immediately after creating the project")
        self.analyze_now.setChecked(True)
        layout.addWidget(self.analyze_now)
        self.registerField("analyzeNow", self.analyze_now)
        
        # Create plugin info area
        info_group = QGroupBox("Plugin Information")
        info_layout = QVBoxLayout()
        self.plugin_info_label = QLabel("Select a plugin to see details.")
        info_layout.addWidget(self.plugin_info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.setLayout(layout)
        
        # Connect signals
        self.plugin_list.itemChanged.connect(self.update_selected_plugins)
        self.plugin_list.currentItemChanged.connect(self.update_plugin_info)
    
    def load_plugins(self):
        """Load available plugins into the list."""
        for plugin in self.plugin_manager.plugins:
            item = QListWidget.QListWidgetItem(plugin.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.plugin_list.addItem(item)
    
    def update_selected_plugins(self):
        """Update the list of selected plugins."""
        self.selected_plugins = []
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            if item.checkState() == Qt.Checked:
                self.selected_plugins.append(item.text())
    
    def update_plugin_info(self, current, previous):
        """Update plugin information display."""
        if current:
            for plugin in self.plugin_manager.plugins:
                if plugin.name == current.text():
                    info = f"<p><b>{plugin.name}</b></p>"
                    info += f"<p>{plugin.description}</p>"
                    self.plugin_info_label.setText(info)
                    break
    
    def value(self):
        """Return the selected plugins."""
        return self.selected_plugins


class SummaryPage(QWizardPage):
    """Summary and confirmation page."""
    
    def __init__(self, parent=None):
        super(SummaryPage, self).__init__(parent)
        
        self.setTitle("Project Summary")
        self.setSubTitle("Review your project configuration before creating it.")
        
        # Create layout
        layout = QVBoxLayout()
        
        # Summary text
        self.summary_text = QLabel()
        self.summary_text.setWordWrap(True)
        layout.addWidget(self.summary_text)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Update the summary text when the page is shown."""
        project_name = self.field("projectName")
        project_dir = self.field("projectDirectory")
        plugins = self.field("selectedPlugins")
        
        # Get target details from the target details page
        target_page = self.wizard().page(2)  # TargetDetailsPage is at index 2
        targets = target_page.get_targets()
        
        # Build summary text
        summary = f"<h3>Project: {project_name}</h3>"
        summary += f"<p><b>Location:</b> {project_dir}</p>"
        
        summary += "<p><b>Targets:</b></p>"
        summary += "<ul>"
        for target in targets:
            summary += f"<li>{target['name']}"
            if target['username']:
                summary += f" (@{target['username']})"
            summary += "</li>"
        summary += "</ul>"
        
        summary += "<p><b>Selected Data Sources:</b></p>"
        summary += "<ul>"
        if plugins is None:
            plugins = []
        for plugin in plugins:
            summary += f"<li>{plugin}</li>"
        summary += "</ul>"
        
        analyze_now = self.field("analyzeNow")
        summary += f"<p><b>Analyze immediately:</b> {'Yes' if analyze_now else 'No'}</p>"
        
        summary += "<p>Click Finish to create your project.</p>"
        
        self.summary_text.setText(summary)
=======
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\personProjectWizard.ui'
#
# Created: Fri Jan 31 15:30:24 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_personProjectWizard(object):
    def setupUi(self, personProjectWizard):
        personProjectWizard.setObjectName(_fromUtf8("personProjectWizard"))
        personProjectWizard.resize(898, 702)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/user")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        personProjectWizard.setWindowIcon(icon)
        personProjectWizard.setWizardStyle(QtWidgets.QWizard.ClassicStyle)
        personProjectWizard.setOptions(QtWidgets.QWizard.HelpButtonOnRight)
        self.personProjectWizardPage1 = QtWidgets.QWizardPage()
        self.personProjectWizardPage1.setObjectName(_fromUtf8("personProjectWizardPage1"))
        self.gridLayoutWidget = QtWidgets.QWidget(self.personProjectWizardPage1)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 861, 591))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.personProjectDescriptionValue = QtWidgets.QPlainTextEdit(self.gridLayoutWidget)
        self.personProjectDescriptionValue.setPlainText(_fromUtf8(""))
        self.personProjectDescriptionValue.setObjectName(_fromUtf8("personProjectDescriptionValue"))
        self.gridLayout_3.addWidget(self.personProjectDescriptionValue, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 3, 1, 1, 1)
        self.personProjectNameValue = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.personProjectNameValue.setObjectName(_fromUtf8("personProjectNameValue"))
        self.gridLayout_3.addWidget(self.personProjectNameValue, 0, 1, 1, 1)
        self.personProjectNameLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.personProjectNameLabel.setEnabled(True)
        self.personProjectNameLabel.setObjectName(_fromUtf8("personProjectNameLabel"))
        self.gridLayout_3.addWidget(self.personProjectNameLabel, 0, 0, 1, 1)
        self.personProjectKeywordsValue = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.personProjectKeywordsValue.setObjectName(_fromUtf8("personProjectKeywordsValue"))
        self.gridLayout_3.addWidget(self.personProjectKeywordsValue, 1, 1, 1, 1)
        self.personProjectDescriptionLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.personProjectDescriptionLabel.sizePolicy().hasHeightForWidth())
        self.personProjectDescriptionLabel.setSizePolicy(sizePolicy)
        self.personProjectDescriptionLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.personProjectDescriptionLabel.setObjectName(_fromUtf8("personProjectDescriptionLabel"))
        self.gridLayout_3.addWidget(self.personProjectDescriptionLabel, 2, 0, 1, 1)
        self.personProkectKeywordsLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.personProkectKeywordsLabel.setObjectName(_fromUtf8("personProkectKeywordsLabel"))
        self.gridLayout_3.addWidget(self.personProkectKeywordsLabel, 1, 0, 1, 1)
        personProjectWizard.addPage(self.personProjectWizardPage1)
        self.personProjectWizardPage2 = QtWidgets.QWizardPage()
        self.personProjectWizardPage2.setObjectName(_fromUtf8("personProjectWizardPage2"))
        self.gridLayout = QtWidgets.QGridLayout(self.personProjectWizardPage2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btnAddTarget = QtWidgets.QPushButton(self.personProjectWizardPage2)
        self.btnAddTarget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btnAddTarget.setStyleSheet(_fromUtf8(""))
        self.btnAddTarget.setObjectName(_fromUtf8("btnAddTarget"))
        self.horizontalLayout.addWidget(self.btnAddTarget)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 3, 1, 1)
        self.personProjectSelectedTargetsTable = QtWidgets.QTableView(self.personProjectWizardPage2)
        self.personProjectSelectedTargetsTable.setDragEnabled(False)
        self.personProjectSelectedTargetsTable.setDragDropOverwriteMode(True)
        self.personProjectSelectedTargetsTable.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.personProjectSelectedTargetsTable.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.personProjectSelectedTargetsTable.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.personProjectSelectedTargetsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.personProjectSelectedTargetsTable.setSortingEnabled(True)
        self.personProjectSelectedTargetsTable.setObjectName(_fromUtf8("personProjectSelectedTargetsTable"))
        self.personProjectSelectedTargetsTable.horizontalHeader().setCascadingSectionResizes(True)
        self.personProjectSelectedTargetsTable.horizontalHeader().setStretchLastSection(True)
        self.personProjectSelectedTargetsTable.verticalHeader().setVisible(False)
        self.personProjectSelectedTargetsTable.verticalHeader().setCascadingSectionResizes(True)
        self.gridLayout.addWidget(self.personProjectSelectedTargetsTable, 8, 2, 1, 2)
        self.personProjectTargetSeperatorLine = QtWidgets.QFrame(self.personProjectWizardPage2)
        self.personProjectTargetSeperatorLine.setLineWidth(4)
        self.personProjectTargetSeperatorLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.personProjectTargetSeperatorLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.personProjectTargetSeperatorLine.setObjectName(_fromUtf8("personProjectTargetSeperatorLine"))
        self.gridLayout.addWidget(self.personProjectTargetSeperatorLine, 6, 1, 1, 3)
        self.personProjectSearchResultsTable = QtWidgets.QTableView(self.personProjectWizardPage2)
        self.personProjectSearchResultsTable.setDragEnabled(True)
        self.personProjectSearchResultsTable.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.personProjectSearchResultsTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.personProjectSearchResultsTable.setSortingEnabled(True)
        self.personProjectSearchResultsTable.setObjectName(_fromUtf8("personProjectSearchResultsTable"))
        self.personProjectSearchResultsTable.horizontalHeader().setCascadingSectionResizes(True)
        self.personProjectSearchResultsTable.horizontalHeader().setStretchLastSection(True)
        self.personProjectSearchResultsTable.verticalHeader().setVisible(False)
        self.personProjectSearchResultsTable.verticalHeader().setCascadingSectionResizes(True)
        self.personProjectSearchResultsTable.verticalHeader().setMinimumSectionSize(19)
        self.personProjectSearchResultsTable.verticalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.personProjectSearchResultsTable, 4, 2, 1, 2)
        self.personProjectSearchForLabel = QtWidgets.QLabel(self.personProjectWizardPage2)
        self.personProjectSearchForLabel.setObjectName(_fromUtf8("personProjectSearchForLabel"))
        self.gridLayout.addWidget(self.personProjectSearchForLabel, 0, 0, 1, 2)
        self.personProjectSearchResultsLabel = QtWidgets.QLabel(self.personProjectWizardPage2)
        self.personProjectSearchResultsLabel.setObjectName(_fromUtf8("personProjectSearchResultsLabel"))
        self.gridLayout.addWidget(self.personProjectSearchResultsLabel, 4, 0, 1, 1)
        self.personProjectSelectedTargetsLabel = QtWidgets.QLabel(self.personProjectWizardPage2)
        self.personProjectSelectedTargetsLabel.setObjectName(_fromUtf8("personProjectSelectedTargetsLabel"))
        self.gridLayout.addWidget(self.personProjectSelectedTargetsLabel, 8, 0, 1, 1)
        self.personProjectSearchInLabel = QtWidgets.QLabel(self.personProjectWizardPage2)
        self.personProjectSearchInLabel.setObjectName(_fromUtf8("personProjectSearchInLabel"))
        self.gridLayout.addWidget(self.personProjectSearchInLabel, 1, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 2, 1, 1)
        self.personProjectSearchForDetailsLabel = QtWidgets.QLabel(self.personProjectWizardPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.personProjectSearchForDetailsLabel.sizePolicy().hasHeightForWidth())
        self.personProjectSearchForDetailsLabel.setSizePolicy(sizePolicy)
        self.personProjectSearchForDetailsLabel.setObjectName(_fromUtf8("personProjectSearchForDetailsLabel"))
        self.gridLayout.addWidget(self.personProjectSearchForDetailsLabel, 0, 3, 1, 1)
        self.personProjectAvailablePluginsScrollArea = QtWidgets.QScrollArea(self.personProjectWizardPage2)
        self.personProjectAvailablePluginsScrollArea.setWidgetResizable(True)
        self.personProjectAvailablePluginsScrollArea.setObjectName(_fromUtf8("personProjectAvailablePluginsScrollArea"))
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 98, 91))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.personProjectAvailablePluginsListView = QtWidgets.QListView(self.scrollAreaWidgetContents)
        self.personProjectAvailablePluginsListView.setObjectName(_fromUtf8("personProjectAvailablePluginsListView"))
        self.verticalLayout.addWidget(self.personProjectAvailablePluginsListView)
        self.personProjectAvailablePluginsScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.personProjectAvailablePluginsScrollArea, 1, 2, 1, 2)
        self.personProjectSearchForValue = QtWidgets.QLineEdit(self.personProjectWizardPage2)
        self.personProjectSearchForValue.setObjectName(_fromUtf8("personProjectSearchForValue"))
        self.gridLayout.addWidget(self.personProjectSearchForValue, 0, 2, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.personProjectSearchButton = QtWidgets.QPushButton(self.personProjectWizardPage2)
        self.personProjectSearchButton.setDefault(True)
        self.personProjectSearchButton.setObjectName(_fromUtf8("personProjectSearchButton"))
        self.horizontalLayout_2.addWidget(self.personProjectSearchButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 3, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 5, 2, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 9, 2, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.btnRemoveTarget = QtWidgets.QPushButton(self.personProjectWizardPage2)
        self.btnRemoveTarget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btnRemoveTarget.setStyleSheet(_fromUtf8(""))
        self.btnRemoveTarget.setObjectName(_fromUtf8("btnRemoveTarget"))
        self.horizontalLayout_3.addWidget(self.btnRemoveTarget)
        self.gridLayout.addLayout(self.horizontalLayout_3, 9, 3, 1, 1)
        personProjectWizard.addPage(self.personProjectWizardPage2)
        self.personProjectWizardPage3 = QtWidgets.QWizardPage()
        self.personProjectWizardPage3.setObjectName(_fromUtf8("personProjectWizardPage3"))
        self.personProjectWizardSearchConfigPluginsList = QtWidgets.QListView(self.personProjectWizardPage3)
        self.personProjectWizardSearchConfigPluginsList.setGeometry(QtCore.QRect(0, 0, 256, 531))
        self.personProjectWizardSearchConfigPluginsList.setObjectName(_fromUtf8("personProjectWizardSearchConfigPluginsList"))
        self.searchConfiguration = QtWidgets.QStackedWidget(self.personProjectWizardPage3)
        self.searchConfiguration.setGeometry(QtCore.QRect(260, 0, 591, 531))
        self.searchConfiguration.setObjectName(_fromUtf8("searchConfiguration"))
        personProjectWizard.addPage(self.personProjectWizardPage3)
        self.personProjectWizardPage4 = QtWidgets.QWizardPage()
        self.personProjectWizardPage4.setObjectName(_fromUtf8("personProjectWizardPage4"))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.personProjectWizardPage4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        personProjectWizard.addPage(self.personProjectWizardPage4)

        self.retranslateUi(personProjectWizard)
        QtCore.QMetaObject.connectSlotsByName(personProjectWizard)

    def retranslateUi(self, personProjectWizard):
        personProjectWizard.setWindowTitle(QtWidgets.QApplication.translate("personProjectWizard", "New Person Project", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage1.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 1 - Set Project Metadata", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage1.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Add project related information", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectNameValue.setPlaceholderText(QtWidgets.QApplication.translate("personProjectWizard", "Add a name for your project", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectNameLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Project Name ", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectKeywordsValue.setPlaceholderText(QtWidgets.QApplication.translate("personProjectWizard", "Add comma seperated keywords for your project", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectDescriptionLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Description", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProkectKeywordsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Keywords", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage2.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 2 - Set the target", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage2.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Search for the person you want to track using the available plugins and add it to the <font color=\"red\">selected targets</font> by drag and drop or by clicking \"Add To Targets\"", None, QtWidgets.QApplication.UnicodeUTF8))
        self.btnAddTarget.setText(QtWidgets.QApplication.translate("personProjectWizard", "Add To Targets", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSearchForLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600;\">Search for</span></p></body></html>", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSearchResultsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600;\">Search Results </span></p></body></html>", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSelectedTargetsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600; color:#ff0000;\">Selected Targets</span></p></body></html>", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSearchInLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "<html><head/><body><p><span style=\" font-weight:600;\">Search In</span></p></body></html>", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSearchForDetailsLabel.setText(QtWidgets.QApplication.translate("personProjectWizard", "Search by username, mail, full name, id", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSearchButton.setToolTip(QtWidgets.QApplication.translate("personProjectWizard", "Search for targets in the selected plugins", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectSearchButton.setText(QtWidgets.QApplication.translate("personProjectWizard", "Search", None, QtWidgets.QApplication.UnicodeUTF8))
        self.btnRemoveTarget.setText(QtWidgets.QApplication.translate("personProjectWizard", "Remove Selected", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage3.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 3 - Set Parameters", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage3.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Provide the necessary search parameters for the plugins you are using", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage4.setTitle(QtWidgets.QApplication.translate("personProjectWizard", "Step 4  - Finalize Project", None, QtWidgets.QApplication.UnicodeUTF8))
        self.personProjectWizardPage4.setSubTitle(QtWidgets.QApplication.translate("personProjectWizard", "Click Finish to save the Project Configuration ", None, QtWidgets.QApplication.UnicodeUTF8))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    personProjectWizard = QtWidgets.QWizard()
    ui = Ui_personProjectWizard()
    ui.setupUi(personProjectWizard)
    personProjectWizard.show()
    sys.exit(app.exec_())

>>>>>>> gs-ai-patch-1
