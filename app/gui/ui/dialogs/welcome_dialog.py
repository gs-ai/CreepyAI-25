"""
Welcome Dialog for CreepyAI
Displayed when the application is first run or when requested
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWizard, QWizardPage, QCheckBox, QLineEdit, QFileDialog,
    QComboBox, QStackedWidget, QWidget, QFrame, QScrollArea,
    QSizePolicy, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QPixmap, QFont, QIcon

from app.core.include.button_styles import ButtonStyles

logger = logging.getLogger(__name__)

class WelcomeDialog(QWizard):
    """Welcome wizard that guides new users through the initial setup"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to CreepyAI")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Set window size
        self.resize(700, 500)
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(PluginSetupPage())
        self.addPage(DataDirectoryPage())
        self.addPage(PrivacySettingsPage())
        self.addPage(CompletionPage())
        
        # Set page titles
        self.setButtonText(QWizard.FinishButton, "Get Started")
        self.setOption(QWizard.HaveHelpButton, False)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        
        # Set button styles
        self.style_buttons()
        
        # Load the settings to check if this is first run
        settings = QSettings("CreepyAI", "Application")
        self.is_first_run = settings.value("firstRun", True, bool)
    
    def style_buttons(self):
        """Apply consistent styling to wizard buttons"""
        ButtonStyles.primary_button(self.button(QWizard.FinishButton))
        ButtonStyles.secondary_button(self.button(QWizard.BackButton))
        ButtonStyles.secondary_button(self.button(QWizard.NextButton))
        ButtonStyles.secondary_button(self.button(QWizard.CancelButton))
    
    def accept(self):
        """Called when the wizard is accepted"""
        # Save the settings
        settings = QSettings("CreepyAI", "Application")
        settings.setValue("firstRun", False)
        
        # Set configuration values from user inputs
        don_show_again = self.field("dontShowOnStartup")
        if don_show_again:
            settings.setValue("skipWelcomeDialog", True)
            
        # Get data directory
        data_directory = self.field("dataDirectory")
        if data_directory:
            settings.setValue("dataDirectory", data_directory)
        
        # Get privacy settings
        collect_usage_data = self.field("collectUsageData")
        settings.setValue("collectUsageData", collect_usage_data)
        
        # Call parent accept to finish
        super().accept()

class WelcomePage(QWizardPage):
    """Welcome page with introduction to CreepyAI"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to CreepyAI")
        self.setSubTitle("Open Source Intelligence Location Analysis Tool")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join("app", "resources", "images", "creepyai-logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Welcome message
        welcome_label = QLabel(
            "<p style='font-size: 14px;'>CreepyAI helps you analyze and visualize location data from various sources, "
            "including social media platforms.</p>"
            "<p style='font-size: 14px;'>This wizard will help you set up the application and configure the plugins.</p>"
        )
        welcome_label.setWordWrap(True)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Version information
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show this dialog on startup")
        self.dont_show_checkbox.setChecked(False)
        layout.addWidget(self.dont_show_checkbox)
        
        # Spacing at the bottom
        layout.addStretch()
        
        # Register field for the checkbox
        self.registerField("dontShowOnStartup", self.dont_show_checkbox)

class PluginSetupPage(QWizardPage):
    """Page for setting up and configuring plugins"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Plugin Configuration")
        self.setSubTitle("Configure the data source plugins you want to use")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Plugin description
        description_label = QLabel(
            "<p>CreepyAI uses plugins to collect location data from various sources.</p>"
            "<p>Select the plugins you want to enable and configure:</p>"
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Create a scroll area for plugins
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        
        # Add plugin checkboxes
        plugins = [
            ("Facebook", "Extract location data from Facebook data exports"),
            ("Instagram", "Extract location data from Instagram data exports"),
            ("Twitter", "Extract location data from Twitter data exports"),
            ("LinkedIn", "Extract location data from LinkedIn data exports"),
            ("Pinterest", "Extract location data from Pinterest data exports"),
            ("Snapchat", "Extract location data from Snapchat data exports"),
            ("TikTok", "Extract location data from TikTok data exports"),
            ("Yelp", "Extract location data from Yelp data exports")
        ]
        
        for name, description in plugins:
            plugin_frame = QFrame()
            plugin_frame.setFrameShape(QFrame.StyledPanel)
            plugin_layout = QVBoxLayout(plugin_frame)
            
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)  # Default to enabled
            self.registerField(f"enable{name}", checkbox)
            
            plugin_layout.addWidget(checkbox)
            
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            plugin_layout.addWidget(desc_label)
            
            scroll_layout.addWidget(plugin_frame)
        
        layout.addWidget(scroll)
        
        # Advanced configuration note
        note_label = QLabel(
            "<p><i>Note: Advanced configuration options for each plugin "
            "will be available in the main application.</i></p>"
        )
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

class DataDirectoryPage(QWizardPage):
    """Page for selecting data directories"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Data Directory")
        self.setSubTitle("Select where CreepyAI will store collected data")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Description
        description_label = QLabel(
            "<p>CreepyAI needs a directory to store collected data, "
            "analysis results, and configuration files.</p>"
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Directory selection
        dir_frame = QFrame()
        dir_layout = QHBoxLayout(dir_frame)
        
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select a directory")
        
        # Set default directory
        default_dir = os.path.join(os.path.expanduser("~"), "CreepyAI-Data")
        self.dir_input.setText(default_dir)
        
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        ButtonStyles.secondary_button(browse_btn)
        dir_layout.addWidget(browse_btn)
        
        layout.addWidget(dir_frame)
        
        # Register field
        self.registerField("dataDirectory*", self.dir_input)
        
        # Additional storage options
        storage_label = QLabel("<p>Storage options:</p>")
        layout.addWidget(storage_label)
        
        self.compress_checkbox = QCheckBox("Compress data when possible to save space")
        self.compress_checkbox.setChecked(True)
        layout.addWidget(self.compress_checkbox)
        
        self.backup_checkbox = QCheckBox("Create automatic backups of important data")
        self.backup_checkbox.setChecked(True)
        layout.addWidget(self.backup_checkbox)
        
        self.encryption_checkbox = QCheckBox("Enable data encryption (recommended)")
        self.encryption_checkbox.setChecked(False)
        layout.addWidget(self.encryption_checkbox)
        
        # Register fields
        self.registerField("compressData", self.compress_checkbox)
        self.registerField("backupData", self.backup_checkbox)
        self.registerField("encryptData", self.encryption_checkbox)
        
        # Add validation note
        note_label = QLabel(
            "<p><i>Note: CreepyAI will create the directory if it doesn't exist. "
            "You'll need appropriate permissions for the selected location.</i></p>"
        )
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        layout.addStretch()
    
    def browse_directory(self):
        """Open dialog to select directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Data Directory", self.dir_input.text()
        )
        if directory:
            self.dir_input.setText(directory)

class PrivacySettingsPage(QWizardPage):
    """Page for privacy and data collection settings"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Privacy Settings")
        self.setSubTitle("Configure privacy and data collection preferences")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Description
        description_label = QLabel(
            "<p>CreepyAI respects your privacy. Configure how the application "
            "handles your data and what information is collected.</p>"
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Privacy options frame
        privacy_frame = QFrame()
        privacy_frame.setFrameShape(QFrame.StyledPanel)
        privacy_layout = QVBoxLayout(privacy_frame)
        
        # Usage data option
        self.usage_checkbox = QCheckBox(
            "Allow collection of anonymous usage data to improve the application"
        )
        self.usage_checkbox.setChecked(False)
        privacy_layout.addWidget(self.usage_checkbox)
        
        usage_details = QLabel(
            "<p><small>This includes information about features used, errors encountered, "
            "and general performance metrics. No personal data or analysis results "
            "are ever shared.</small></p>"
        )
        usage_details.setWordWrap(True)
        usage_details.setIndent(20)
        privacy_layout.addWidget(usage_details)
        
        # Crash reporting option
        self.crash_checkbox = QCheckBox(
            "Enable automatic crash reporting"
        )
        self.crash_checkbox.setChecked(True)
        privacy_layout.addWidget(self.crash_checkbox)
        
        crash_details = QLabel(
            "<p><small>When enabled, CreepyAI will send anonymous crash reports to help "
            "developers identify and fix issues. No personal data is included.</small></p>"
        )
        crash_details.setWordWrap(True)
        crash_details.setIndent(20)
        privacy_layout.addWidget(crash_details)
        
        # Update checking
        self.update_checkbox = QCheckBox(
            "Check for updates automatically"
        )
        self.update_checkbox.setChecked(True)
        privacy_layout.addWidget(self.update_checkbox)
        
        layout.addWidget(privacy_frame)
        
        # Register fields
        self.registerField("collectUsageData", self.usage_checkbox)
        self.registerField("enableCrashReports", self.crash_checkbox)
        self.registerField("checkForUpdates", self.update_checkbox)
        
        # Privacy policy link
        privacy_link = QLabel(
            "<p><a href='https://creepyai.example.com/privacy'>View our full privacy policy</a></p>"
        )
        privacy_link.setOpenExternalLinks(True)
        layout.addWidget(privacy_link)
        
        layout.addStretch()

class CompletionPage(QWizardPage):
    """Final page shown when setup is complete"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete")
        self.setSubTitle("Your CreepyAI installation is ready to use")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Completion message
        complete_label = QLabel(
            "<p style='font-size: 14px;'>Congratulations! CreepyAI has been configured successfully.</p>"
            "<p>You're now ready to start analyzing location data. Here are some next steps to get started:</p>"
        )
        complete_label.setWordWrap(True)
        layout.addWidget(complete_label)
        
        # Next steps list
        steps_list = QLabel(
            "<ol>"
            "<li>Import data from social media exports</li>"
            "<li>Configure additional plugins as needed</li>"
            "<li>View your data on the interactive map</li>"
            "<li>Export your findings for reports or further analysis</li>"
            "</ol>"
        )
        steps_list.setWordWrap(True)
        layout.addWidget(steps_list)
        
        # Additional resources
        resources_label = QLabel(
            "<p>Additional Resources:</p>"
        )
        resources_label.setWordWrap(True)
        layout.addWidget(resources_label)
        
        # Resource links
        links_label = QLabel(
            "<ul>"
            "<li><a href='https://creepyai.example.com/docs'>Documentation</a></li>"
            "<li><a href='https://creepyai.example.com/tutorials'>Tutorials</a></li>"
            "<li><a href='https://creepyai.example.com/faq'>Frequently Asked Questions</a></li>"
            "</ul>"
        )
        links_label.setOpenExternalLinks(True)
        links_label.setWordWrap(True)
        layout.addWidget(links_label)
        
        layout.addStretch()
        
        # Register field for completion
        self.registerField("setupComplete", self.create_invisible_checkbox(True))
    
    def create_invisible_checkbox(self, checked: bool) -> QCheckBox:
        """Create an invisible checkbox with initial state"""
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.setVisible(False)
        return checkbox
