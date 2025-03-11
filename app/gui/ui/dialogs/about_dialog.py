"""
About Dialog for CreepyAI
Shows application version, credits, and license information
"""

import os
import sys
import logging
from typing import Dict, List, Any

from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QDialogButtonBox, QWidget, 
    QScrollArea, QSizePolicy, QGroupBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon

from app.core.include.button_styles import ButtonStyles

logger = logging.getLogger(__name__)

class AboutDialog(QDialog):
    """Dialog showing information about the application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About CreepyAI")
        self.resize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.app_version = "1.0.0"
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabbed interface
        tabs = QTabWidget()
        
        # Add tabs
        tabs.addTab(self.create_about_tab(), "About")
        tabs.addTab(self.create_credits_tab(), "Credits")
        tabs.addTab(self.create_license_tab(), "License")
        tabs.addTab(self.create_plugins_tab(), "Plugins")
        
        layout.addWidget(tabs)
        
        # Add OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ButtonStyles.primary_button(ok_button)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
    
    def create_about_tab(self) -> QWidget:
        """Create the About tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # App logo
        logo_label = QLabel()
        logo_path = os.path.join("app", "resources", "images", "creepyai-logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # App name and version
        name_label = QLabel("CreepyAI")
        name_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        name_label.setFont(font)
        layout.addWidget(name_label)
        
        version_label = QLabel(f"Version {self.app_version}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # App description
        desc_label = QLabel(
            "<p>CreepyAI is an open-source OSINT (Open Source Intelligence) tool "
            "designed to collect, analyze, and visualize location data from various sources, "
            "including social media platforms.</p>"
            "<p>This application is designed for educational and research purposes only.</p>"
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # System info
        sys_info = self.get_system_info()
        sys_group = QGroupBox("System Information")
        sys_layout = QVBoxLayout(sys_group)
        
        for label, value in sys_info.items():
            info_layout = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            info_layout.addWidget(label_widget)
            
            value_widget = QLabel(value)
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            info_layout.addWidget(value_widget)
            
            sys_layout.addLayout(info_layout)
        
        layout.addWidget(sys_group)
        
        # Website link
        website_label = QLabel(
            "<p><a href='https://creepyai.example.com'>Visit CreepyAI Website</a></p>"
        )
        website_label.setOpenExternalLinks(True)
        website_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(website_label)
        
        layout.addStretch()
        
        return tab
    
    def create_credits_tab(self) -> QWidget:
        """Create the Credits tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Developers section
        dev_group = QGroupBox("Development Team")
        dev_layout = QVBoxLayout(dev_group)
        
        dev_text = QLabel(
            "<p><b>Lead Developer:</b> John Doe</p>"
            "<p><b>Contributors:</b></p>"
            "<ul>"
            "<li>Jane Smith - Plugin Framework</li>"
            "<li>Alex Johnson - Map Integration</li>"
            "<li>Sam Wilson - UI Design</li>"
            "</ul>"
        )
        dev_text.setWordWrap(True)
        dev_layout.addWidget(dev_text)
        
        layout.addWidget(dev_group)
        
        # Libraries and frameworks
        libs_group = QGroupBox("Libraries & Frameworks")
        libs_layout = QVBoxLayout(libs_group)
        
        libs_text = QLabel(
            "<p>CreepyAI relies on the following open-source libraries and frameworks:</p>"
            "<ul>"
            "<li>Python - Programming language</li>"
            "<li>PyQt5 - GUI framework</li>"
            "<li>Leaflet.js - Interactive maps</li>"
            "<li>BeautifulSoup4 - Web scraping</li>"
            "<li>Requests - HTTP client</li>"
            "<li>SQLite - Database</li>"
            "</ul>"
            "<p>And many other valuable tools and libraries.</p>"
        )
        libs_text.setWordWrap(True)
        libs_layout.addWidget(libs_text)
        
        layout.addWidget(libs_group)
        
        # Icons and graphics
        icons_group = QGroupBox("Icons & Graphics")
        icons_layout = QVBoxLayout(icons_group)
        
        icons_text = QLabel(
            "<p>Icons used in the application are from:</p>"
            "<ul>"
            "<li>Icons8 - <a href='https://icons8.com'>https://icons8.com</a></li>"
            "<li>Font Awesome - <a href='https://fontawesome.com'>https://fontawesome.com</a></li>"
            "</ul>"
        )
        icons_text.setOpenExternalLinks(True)
        icons_text.setWordWrap(True)
        icons_layout.addWidget(icons_text)
        
        layout.addWidget(icons_group)
        
        layout.addStretch()
        
        return tab
    
    def create_license_tab(self) -> QWidget:
        """Create the License tab content"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # License notice
        license_notice = QLabel(
            "<p>CreepyAI is licensed under the GNU General Public License v3.0 (GPL-3.0)</p>"
        )
        license_notice.setWordWrap(True)
        layout.addWidget(license_notice)
        
        # License text
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        
        license_path = os.path.join("LICENSE")
        if os.path.exists(license_path):
            with open(license_path, 'r') as f:
                license_text.setPlainText(f.read())
        else:
            license_text.setPlainText("License file not found.")
        
        layout.addWidget(license_text)
        
        # Disclaimer
        disclaimer_label = QLabel(
            "<p><b>Disclaimer:</b> This software is provided for educational and research "
            "purposes only. The developers assume no liability and are not responsible "
            "for any misuse or damage caused by this program.</p>"
        )
        disclaimer_label.setWordWrap(True)
        layout.addWidget(disclaimer_label)
        
        return tab
    
    def create_plugins_tab(self) -> QWidget:
        """Create the Plugins tab content"""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Plugins section
        plugins_label = QLabel(
            "<p>CreepyAI includes the following plugins:</p>"
        )
        plugins_label.setWordWrap(True)
        layout.addWidget(plugins_label)
        
        # Get available plugins
        try:
            from app.plugin_registry import instantiate_plugins
            plugins = instantiate_plugins()
            
            # Add info for each plugin
            for plugin in plugins:
                plugin_group = QGroupBox(plugin.name)
                plugin_layout = QVBoxLayout(plugin_group)
                
                plugin_info = QLabel(
                    f"<p><b>Description:</b> {plugin.description}</p>"
                    f"<p><b>Version:</b> {getattr(plugin, 'version', '1.0.0')}</p>"
                )
                plugin_info.setWordWrap(True)
                plugin_layout.addWidget(plugin_info)
                
                # Add author if available
                if hasattr(plugin, 'author'):
                    author_info = QLabel(f"<p><b>Author:</b> {plugin.author}</p>")
                    author_info.setWordWrap(True)
                    plugin_layout.addWidget(author_info)
                
                layout.addWidget(plugin_group)
        except Exception as e:
            error_label = QLabel(f"Error loading plugin information: {str(e)}")
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
        
        layout.addStretch()
        tab.setWidget(content_widget)
        
        return tab
    
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        info = {}
        
        # Python version
        info["Python Version"] = sys.version.split()[0]
        
        # PyQt version
        try:
            from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
            info["Qt Version"] = QT_VERSION_STR
            info["PyQt Version"] = PYQT_VERSION_STR
        except ImportError:
            info["Qt/PyQt Version"] = "Unknown"
        
        # OS information
        info["Operating System"] = f"{sys.platform}"
        
        # CPU Architecture
        import platform
        info["Architecture"] = platform.architecture()[0]
        
        return info
